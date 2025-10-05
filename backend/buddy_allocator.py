"""
Improvised Memory Manager - Buddy System with Best-Fit Allocation
Combines buddy system principles with best-fit allocation and compaction
"""

import math
from typing import List, Dict, Optional, Tuple


class MemoryBlock:
    """Represents a block of memory"""
    
    def __init__(self, start: int, size: int, is_free: bool = True, process_name: str = None):
        self.start = start
        self.size = size
        self.is_free = is_free
        self.process_name = process_name
    
    @property
    def end(self) -> int:
        """End address of the block"""
        return self.start + self.size
    
    def to_dict(self) -> Dict:
        """Convert block to dictionary for JSON serialization"""
        return {
            "start": self.start,
            "size": self.size,
            "is_free": self.is_free,
            "process_name": self.process_name,
            "end": self.end
        }
    
    def __repr__(self):
        status = "FREE" if self.is_free else f"ALLOCATED({self.process_name})"
        return f"Block[{self.start}-{self.end}]: {self.size}KB {status}"


class ImprovisedMemoryManager:
    """
    Improvised Memory Manager combining:
    - Best-fit allocation strategy
    - Memory compaction
    - Buddy system style power-of-2 sizing
    """
    
    def __init__(self, total_memory: int = 1024):
        """
        Initialize memory manager
        
        Args:
            total_memory: Total memory size in KB
        """
        self.total_memory = total_memory
        self.blocks: List[MemoryBlock] = []
        self.process_map: Dict[str, MemoryBlock] = {}
        self._initialize_memory()
    
    def _initialize_memory(self):
        """Initialize memory with a single free block"""
        self.blocks = [MemoryBlock(0, self.total_memory, is_free=True)]
        self.process_map = {}
    
    def _round_to_power_of_2(self, size: int) -> int:
        """
        Round size up to nearest power of 2 (buddy system style)
        
        Args:
            size: Original size
            
        Returns:
            Rounded size (power of 2)
        """
        if size <= 0:
            return 1
        return 2 ** math.ceil(math.log2(size))
    
    def _find_best_fit(self, size: int) -> Optional[int]:
        """
        Find the best-fit free block for the given size
        
        Args:
            size: Required size
            
        Returns:
            Index of best-fit block or None if not found
        """
        best_idx = None
        best_size = float('inf')
        
        for idx, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                if block.size < best_size:
                    best_size = block.size
                    best_idx = idx
        
        return best_idx
    
    def allocate(self, process_name: str, size: int, use_buddy: bool = True) -> Tuple[bool, str, Optional[int]]:
        """
        Allocate memory to a process using best-fit strategy
        
        Args:
            process_name: Name of the process
            size: Required memory size
            use_buddy: Whether to use buddy system rounding
            
        Returns:
            Tuple of (success, message, start_address)
        """
        # Check if process already exists
        if process_name in self.process_map:
            return False, f"Process '{process_name}' already allocated", None
        
        # Round to power of 2 if using buddy system
        actual_size = self._round_to_power_of_2(size) if use_buddy else size
        
        # Find best-fit block
        best_idx = self._find_best_fit(actual_size)
        
        if best_idx is None:
            return False, "No suitable free block found. Try compaction.", None
        
        # Get the block
        block = self.blocks[best_idx]
        start_address = block.start
        
        # Split the block if it's larger than needed
        if block.size > actual_size:
            # Create allocated block
            allocated_block = MemoryBlock(block.start, actual_size, is_free=False, process_name=process_name)
            # Create remaining free block
            remaining_block = MemoryBlock(block.start + actual_size, block.size - actual_size, is_free=True)
            
            # Replace the original block with split blocks
            self.blocks[best_idx] = allocated_block
            self.blocks.insert(best_idx + 1, remaining_block)
        else:
            # Use the entire block
            block.is_free = False
            block.process_name = process_name
        
        # Add to process map
        self.process_map[process_name] = self.blocks[best_idx]
        
        return True, f"Process '{process_name}' allocated {actual_size}KB", start_address
    
    def deallocate(self, process_name: str) -> Tuple[bool, str]:
        """
        Deallocate memory for a process
        
        Args:
            process_name: Name of the process to deallocate
            
        Returns:
            Tuple of (success, message)
        """
        if process_name not in self.process_map:
            return False, f"Process '{process_name}' not found"
        
        # Find and free the block
        for block in self.blocks:
            if not block.is_free and block.process_name == process_name:
                block.is_free = True
                block.process_name = None
                break
        
        # Remove from process map
        del self.process_map[process_name]
        
        # Merge adjacent free blocks
        self._merge_free_blocks()
        
        return True, f"Process '{process_name}' deallocated"
    
    def _merge_free_blocks(self):
        """Merge adjacent free blocks to reduce fragmentation"""
        if len(self.blocks) <= 1:
            return
        
        merged = []
        i = 0
        
        while i < len(self.blocks):
            current = self.blocks[i]
            
            # Look ahead to merge consecutive free blocks
            if current.is_free:
                j = i + 1
                while j < len(self.blocks) and self.blocks[j].is_free:
                    current.size += self.blocks[j].size
                    j += 1
                i = j
            else:
                i += 1
            
            merged.append(current)
        
        self.blocks = merged
    
    def compact(self) -> Tuple[bool, str, int]:
        """
        Compact memory by moving all allocated blocks to the beginning
        
        Returns:
            Tuple of (success, message, moved_count)
        """
        allocated_blocks = [b for b in self.blocks if not b.is_free]
        
        if not allocated_blocks:
            return False, "No allocated blocks to compact", 0
        
        # Create new block list
        new_blocks = []
        current_address = 0
        
        # Place all allocated blocks contiguously
        for block in allocated_blocks:
            new_block = MemoryBlock(
                current_address,
                block.size,
                is_free=False,
                process_name=block.process_name
            )
            new_blocks.append(new_block)
            
            # Update process map
            self.process_map[block.process_name] = new_block
            
            current_address += block.size
        
        # Add single free block at the end
        free_space = self.total_memory - current_address
        if free_space > 0:
            new_blocks.append(MemoryBlock(current_address, free_space, is_free=True))
        
        self.blocks = new_blocks
        
        return True, f"Memory compacted successfully", len(allocated_blocks)
    
    def get_used_memory(self) -> int:
        """Get total used memory"""
        return sum(block.size for block in self.blocks if not block.is_free)
    
    def get_free_memory(self) -> int:
        """Get total free memory"""
        return sum(block.size for block in self.blocks if block.is_free)
    
    def get_fragmentation_ratio(self) -> float:
        """
        Calculate fragmentation ratio
        
        Returns:
            Fragmentation ratio (0-1)
        """
        free_blocks = [b for b in self.blocks if b.is_free]
        if len(free_blocks) <= 1:
            return 0.0
        return (len(free_blocks) - 1) / len(self.blocks)
    
    def get_status(self) -> Dict:
        """
        Get current memory status
        
        Returns:
            Dictionary with memory statistics
        """
        return {
            "total_memory": self.total_memory,
            "used_memory": self.get_used_memory(),
            "free_memory": self.get_free_memory(),
            "blocks": [block.to_dict() for block in self.blocks],
            "active_processes": len(self.process_map),
            "fragmentation": round(self.get_fragmentation_ratio() * 100, 2)
        }
    
    def reset(self, new_total_memory: int = None):
        """
        Reset memory manager
        
        Args:
            new_total_memory: New total memory size (optional)
        """
        if new_total_memory:
            self.total_memory = new_total_memory
        self._initialize_memory()


# Example usage and testing
if __name__ == "__main__":
    print("=== Improvised Memory Manager Demo ===\n")
    
    # Initialize with 1024 KB
    manager = ImprovisedMemoryManager(1024)
    print(f"Initialized: {manager.get_status()}\n")
    
    # Allocate some processes
    processes = [
        ("Chrome", 256),
        ("VSCode", 128),
        ("Spotify", 64),
        ("Terminal", 32)
    ]
    
    for name, size in processes:
        success, msg, addr = manager.allocate(name, size)
        print(f"{msg} at address {addr}")
    
    print(f"\nAfter allocation: {manager.get_status()}\n")
    
    # Deallocate some processes
    manager.deallocate("VSCode")
    manager.deallocate("Terminal")
    print(f"After deallocation: {manager.get_status()}\n")
    
    # Try allocation that might fail
    success, msg, addr = manager.allocate("BigApp", 512)
    print(f"{msg}\n")
    
    # Compact memory
    success, msg, moved = manager.compact()
    print(f"{msg} - Moved {moved} processes")
    print(f"After compaction: {manager.get_status()}\n")
    
    # Now try the big allocation again
    success, msg, addr = manager.allocate("BigApp", 512)
    print(f"{msg} at address {addr}")
    print(f"\nFinal state: {manager.get_status()}")
"""
Improvised Memory Manager - Buddy System with Best-Fit Allocation
"""

import math
from typing import List, Dict, Optional, Tuple


class MemoryBlock:
    def __init__(self, start: int, size: int, is_free: bool = True, process_name: str = None):
        self.start = start
        self.size = size
        self.is_free = is_free
        self.process_name = process_name

    @property
    def end(self) -> int:
        return self.start + self.size

    def to_dict(self) -> Dict:
        return {"start": self.start, "size": self.size, "is_free": self.is_free,
                "process_name": self.process_name, "end": self.end}

    def __repr__(self):
        status = "FREE" if self.is_free else f"ALLOCATED({self.process_name})"
        return f"Block[{self.start}-{self.end}]: {self.size}KB {status}"


class ImprovisedMemoryManager:
    def __init__(self, total_memory: int = 1024):
        if total_memory <= 0:
            raise ValueError("total_memory must be > 0")
        self.total_memory = total_memory
        self.blocks: List[MemoryBlock] = []
        self.process_map: Dict[str, MemoryBlock] = {}
        self._initialize_memory()

    def _initialize_memory(self):
        self.blocks = [MemoryBlock(0, self.total_memory, is_free=True)]
        self.process_map = {}

    @staticmethod
    def _round_to_power_of_2(size: int) -> int:
        if size <= 0:
            return 1
        if size == 1:
            return 1
        return 2 ** math.ceil(math.log2(size))

    def _find_best_fit(self, size: int) -> Optional[int]:
        best_idx = None
        best_size = float("inf")
        for idx, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                if block.size < best_size:
                    best_size = block.size
                    best_idx = idx
        return best_idx

    def _merge_free_blocks(self):
        if len(self.blocks) <= 1:
            return
        merged: List[MemoryBlock] = []
        i = 0
        while i < len(self.blocks):
            current = self.blocks[i]
            if current.is_free:
                j = i + 1
                total_size = current.size
                while j < len(self.blocks) and self.blocks[j].is_free:
                    total_size += self.blocks[j].size
                    j += 1
                merged.append(MemoryBlock(current.start, total_size, is_free=True))
                i = j
            else:
                merged.append(current)
                i += 1
        self.blocks = merged

    def allocate(self, process_name: str, size: int, use_buddy: bool = True) -> Tuple[bool, str, Optional[int]]:
        if not process_name or not process_name.strip():
            return False, "Process name cannot be empty", None
        if size <= 0:
            return False, "Size must be greater than 0", None
        if process_name in self.process_map:
            return False, f"Process '{process_name}' is already allocated", None

        actual_size = self._round_to_power_of_2(size) if use_buddy else size
        if actual_size > self.total_memory:
            return False, f"Requested size ({actual_size} KB) exceeds total memory ({self.total_memory} KB)", None

        best_idx = self._find_best_fit(actual_size)
        if best_idx is None:
            if len(self.process_map) > 0:
                self.compact()
                best_idx = self._find_best_fit(actual_size)
            if best_idx is None:
                return False, f"No suitable free block for {actual_size} KB. Try manual compaction.", None

        block = self.blocks[best_idx]
        start_address = block.start

        if block.size > actual_size:
            allocated_block = MemoryBlock(block.start, actual_size, is_free=False, process_name=process_name)
            remaining_block = MemoryBlock(block.start + actual_size, block.size - actual_size, is_free=True)
            self.blocks[best_idx] = allocated_block
            self.blocks.insert(best_idx + 1, remaining_block)
            self.process_map[process_name] = self.blocks[best_idx]
        else:
            block.is_free = False
            block.process_name = process_name
            self.process_map[process_name] = block

        buddy_note = f" (rounded from {size} KB)" if use_buddy and actual_size != size else ""
        return True, f"Process '{process_name}' allocated {actual_size} KB{buddy_note} at address {start_address}", start_address

    def deallocate(self, process_name: str) -> Tuple[bool, str]:
        if process_name not in self.process_map:
            return False, f"Process '{process_name}' not found"
        target = self.process_map[process_name]
        for block in self.blocks:
            if block is target or (not block.is_free and block.process_name == process_name and block.start == target.start):
                block.is_free = True
                block.process_name = None
                break
        del self.process_map[process_name]
        self._merge_free_blocks()
        return True, f"Process '{process_name}' deallocated successfully"

    def compact(self) -> Tuple[bool, str, int]:
        allocated_blocks = [b for b in self.blocks if not b.is_free]
        if not allocated_blocks:
            return False, "No allocated blocks to compact", 0
        new_blocks: List[MemoryBlock] = []
        current_address = 0
        moved = 0
        for block in allocated_blocks:
            new_block = MemoryBlock(current_address, block.size, is_free=False, process_name=block.process_name)
            new_blocks.append(new_block)
            self.process_map[block.process_name] = new_block
            if new_block.start != block.start:
                moved += 1
            current_address += block.size
        free_space = self.total_memory - current_address
        if free_space > 0:
            new_blocks.append(MemoryBlock(current_address, free_space, is_free=True))
        self.blocks = new_blocks
        return True, f"Memory compacted. {moved} block(s) relocated.", moved

    def get_used_memory(self) -> int:
        return sum(b.size for b in self.blocks if not b.is_free)

    def get_free_memory(self) -> int:
        return sum(b.size for b in self.blocks if b.is_free)

    def get_fragmentation_ratio(self) -> float:
        free_blocks = [b for b in self.blocks if b.is_free]
        if len(free_blocks) <= 1:
            return 0.0
        total_free = self.get_free_memory()
        if total_free == 0:
            return 0.0
        largest_free = max(b.size for b in free_blocks)
        return round(1.0 - (largest_free / total_free), 4)

    def get_status(self) -> Dict:
        return {
            "total_memory": self.total_memory,
            "used_memory": self.get_used_memory(),
            "free_memory": self.get_free_memory(),
            "blocks": [b.to_dict() for b in self.blocks],
            "active_processes": len(self.process_map),
            "fragmentation": round(self.get_fragmentation_ratio() * 100, 2),
            "process_list": [
                {"name": name, "size": block.size, "start": block.start, "end": block.end}
                for name, block in self.process_map.items()
            ],
        }

    def reset(self, new_total_memory: int = None):
        if new_total_memory is not None and new_total_memory > 0:
            self.total_memory = new_total_memory
        self._initialize_memory()


if __name__ == "__main__":
    m = ImprovisedMemoryManager(1024)
    for name, size in [("Chrome", 256), ("VSCode", 128), ("Spotify", 64), ("Terminal", 32)]:
        ok, msg, addr = m.allocate(name, size)
        print(f"{'OK' if ok else 'FAIL'}: {msg}")
    m.deallocate("VSCode")
    m.deallocate("Terminal")
    ok, msg, moved = m.compact()
    print(msg)
    ok, msg, addr = m.allocate("BigApp", 512)
    print(f"{'OK' if ok else 'FAIL'}: {msg}")

"""
Test Suite for Improvised Memory Manager
Tests allocation, deallocation, compaction, and edge cases
"""

import pytest
import sys
import os

# Add parent directory to path to import buddy_allocator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.buddy_allocator import ImprovisedMemoryManager, MemoryBlock


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def memory_manager():
    """Create a fresh memory manager instance for each test"""
    return ImprovisedMemoryManager(total_memory=1024)


@pytest.fixture
def populated_manager():
    """Create a memory manager with some allocated processes"""
    manager = ImprovisedMemoryManager(total_memory=1024)
    manager.allocate("Process1", 128)
    manager.allocate("Process2", 256)
    manager.allocate("Process3", 64)
    return manager


# ============================================
# Initialization Tests
# ============================================

class TestInitialization:
    """Test memory manager initialization"""
    
    def test_initialization(self, memory_manager):
        """Test basic initialization"""
        assert memory_manager.total_memory == 1024
        assert len(memory_manager.blocks) == 1
        assert memory_manager.blocks[0].is_free
        assert memory_manager.blocks[0].size == 1024
    
    def test_custom_size_initialization(self):
        """Test initialization with custom size"""
        manager = ImprovisedMemoryManager(2048)
        assert manager.total_memory == 2048
        assert manager.get_free_memory() == 2048
    
    def test_initial_state(self, memory_manager):
        """Test initial memory state"""
        assert memory_manager.get_used_memory() == 0
        assert memory_manager.get_free_memory() == 1024
        assert len(memory_manager.process_map) == 0


# ============================================
# Allocation Tests
# ============================================

class TestAllocation:
    """Test memory allocation"""
    
    def test_simple_allocation(self, memory_manager):
        """Test basic allocation"""
        success, msg, addr = memory_manager.allocate("TestProcess", 128)
        assert success is True
        assert addr == 0
        assert memory_manager.get_used_memory() == 128
    
    def test_buddy_system_rounding(self, memory_manager):
        """Test that buddy system rounds to power of 2"""
        success, msg, addr = memory_manager.allocate("Test", 100, use_buddy=True)
        assert success is True
        # 100 should be rounded to 128 (next power of 2)
        assert memory_manager.get_used_memory() == 128
    
    def test_no_buddy_rounding(self, memory_manager):
        """Test allocation without buddy system rounding"""
        success, msg, addr = memory_manager.allocate("Test", 100, use_buddy=False)
        assert success is True
        assert memory_manager.get_used_memory() == 100
    
    def test_multiple_allocations(self, memory_manager):
        """Test multiple successive allocations"""
        memory_manager.allocate("P1", 128)
        memory_manager.allocate("P2", 256)
        memory_manager.allocate("P3", 64)
        
        assert memory_manager.get_used_memory() == 128 + 256 + 64
        assert len(memory_manager.process_map) == 3
    
    def test_duplicate_process_name(self, memory_manager):
        """Test that duplicate process names are rejected"""
        memory_manager.allocate("Process1", 128)
        success, msg, addr = memory_manager.allocate("Process1", 64)
        assert success is False
        assert "already allocated" in msg
    
    def test_allocation_too_large(self, memory_manager):
        """Test allocation larger than total memory"""
        success, msg, addr = memory_manager.allocate("BigProcess", 2048)
        assert success is False
    
    def test_best_fit_selection(self, memory_manager):
        """Test that best-fit algorithm selects smallest suitable block"""
        # Allocate and deallocate to create fragmentation
        memory_manager.allocate("P1", 128)
        memory_manager.allocate("P2", 256)
        memory_manager.allocate("P3", 128)
        memory_manager.deallocate("P2")  # Creates 256KB hole
        
        # Allocate 64KB - should use best fit
        success, msg, addr = memory_manager.allocate("P4", 64, use_buddy=False)
        assert success is True


# ============================================
# Deallocation Tests
# ============================================

class TestDeallocation:
    """Test memory deallocation"""
    
    def test_simple_deallocation(self, populated_manager):
        """Test basic deallocation"""
        initial_used = populated_manager.get_used_memory()
        success, msg = populated_manager.deallocate("Process1")
        
        assert success is True
        assert populated_manager.get_used_memory() < initial_used
        assert "Process1" not in populated_manager.process_map
    
    def test_deallocate_nonexistent(self, memory_manager):
        """Test deallocating non-existent process"""
        success, msg = memory_manager.deallocate("NonExistent")
        assert success is False
        assert "not found" in msg
    
    def test_merge_adjacent_free_blocks(self, memory_manager):
        """Test that adjacent free blocks are merged"""
        memory_manager.allocate("P1", 128)
        memory_manager.allocate("P2", 128)
        memory_manager.allocate("P3", 128)
        
        # Deallocate middle process
        memory_manager.deallocate("P2")
        block_count_1 = len(memory_manager.blocks)
        
        # Deallocate adjacent process
        memory_manager.deallocate("P1")
        block_count_2 = len(memory_manager.blocks)
        
        # Should merge blocks, reducing count
        assert block_count_2 < block_count_1
    
    def test_deallocate_all(self, populated_manager):
        """Test deallocating all processes"""
        processes = list(populated_manager.process_map.keys())
        for proc in processes:
            populated_manager.deallocate(proc)
        
        assert populated_manager.get_used_memory() == 0
        assert populated_manager.get_free_memory() == 1024
        assert len(populated_manager.process_map) == 0


# ============================================
# Compaction Tests
# ============================================

class TestCompaction:
    """Test memory compaction"""
    
    def test_basic_compaction(self, memory_manager):
        """Test basic compaction functionality"""
        memory_manager.allocate("P1", 128)
        memory_manager.allocate("P2", 128)
        memory_manager.allocate("P3", 128)
        memory_manager.deallocate("P2")
        
        success, msg, moved = memory_manager.compact()
        assert success is True
        assert moved >= 0
        
        # After compaction, all allocated blocks should be at the beginning
        allocated_blocks = [b for b in memory_manager.blocks if not b.is_free]
        if allocated_blocks:
            assert allocated_blocks[0].start == 0
    
    def test_compaction_reduces_fragmentation(self, memory_manager):
        """Test that compaction reduces fragmentation"""
        # Create fragmented memory
        memory_manager.allocate("P1", 64)
        memory_manager.allocate("P2", 64)
        memory_manager.allocate("P3", 64)
        memory_manager.allocate("P4", 64)
        memory_manager.deallocate("P2")
        memory_manager.deallocate("P4")
        
        frag_before = memory_manager.get_fragmentation_ratio()
        memory_manager.compact()
        frag_after = memory_manager.get_fragmentation_ratio()
        
        assert frag_after <= frag_before
    
    def test_compaction_with_no_allocations(self, memory_manager):
        """Test compaction with no allocated blocks"""
        success, msg, moved = memory_manager.compact()
        assert success is False
        assert "No allocated blocks" in msg
    
    def test_compaction_preserves_allocations(self, populated_manager):
        """Test that compaction preserves all allocations"""
        processes_before = set(populated_manager.process_map.keys())
        used_before = populated_manager.get_used_memory()
        
        populated_manager.compact()
        
        processes_after = set(populated_manager.process_map.keys())
        used_after = populated_manager.get_used_memory()
        
        assert processes_before == processes_after
        assert used_before == used_after


# ============================================
# Memory Status Tests
# ============================================

class TestMemoryStatus:
    """Test memory status reporting"""
    
    def test_get_used_memory(self, populated_manager):
        """Test used memory calculation"""
        used = populated_manager.get_used_memory()
        assert used > 0
        assert used <= 1024
    
    def test_get_free_memory(self, populated_manager):
        """Test free memory calculation"""
        free = populated_manager.get_free_memory()
        used = populated_manager.get_used_memory()
        assert free + used == 1024
    
    def test_fragmentation_ratio(self, memory_manager):
        """Test fragmentation ratio calculation"""
        # No fragmentation initially
        assert memory_manager.get_fragmentation_ratio() == 0.0
        
        # Create fragmentation
        memory_manager.allocate("P1", 128)
        memory_manager.allocate("P2", 128)
        memory_manager.allocate("P3", 128)
        memory_manager.deallocate("P2")
        
        frag = memory_manager.get_fragmentation_ratio()
        assert frag > 0.0
    
    def test_get_status(self, populated_manager):
        """Test complete status dictionary"""
        status = populated_manager.get_status()
        
        assert "total_memory" in status
        assert "used_memory" in status
        assert "free_memory" in status
        assert "blocks" in status
        assert "active_processes" in status
        assert "fragmentation" in status
        
        assert status["total_memory"] == 1024
        assert status["active_processes"] == 3


# ============================================
# Edge Cases and Stress Tests
# ============================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_allocate_exact_memory(self, memory_manager):
        """Test allocating exact total memory"""
        success, msg, addr = memory_manager.allocate("Big", 1024, use_buddy=False)
        assert success is True
        assert memory_manager.get_free_memory() == 0
    
    def test_allocate_minimum_size(self, memory_manager):
        """Test allocating minimum size (1 KB)"""
        success, msg, addr = memory_manager.allocate("Tiny", 1, use_buddy=False)
        assert success is True
    
    def test_many_small_allocations(self, memory_manager):
        """Test many small allocations"""
        for i in range(10):
            success, msg, addr = memory_manager.allocate(f"P{i}", 32, use_buddy=False)
            if not success:
                break
        
        assert memory_manager.get_used_memory() > 0
    
    def test_alternating_alloc_dealloc(self, memory_manager):
        """Test alternating allocation and deallocation"""
        for i in range(5):
            memory_manager.allocate(f"P{i}", 128)
            if i > 0:
                memory_manager.deallocate(f"P{i-1}")
        
        # Should have fragmented memory
        assert len(memory_manager.blocks) > 1
    
    def test_reset_functionality(self, populated_manager):
        """Test reset functionality"""
        populated_manager.reset()
        
        assert populated_manager.get_used_memory() == 0
        assert populated_manager.get_free_memory() == 1024
        assert len(populated_manager.process_map) == 0
        assert len(populated_manager.blocks) == 1
    
    def test_reset_with_new_size(self, memory_manager):
        """Test reset with new total memory"""
        memory_manager.allocate("P1", 128)
        memory_manager.reset(2048)
        
        assert memory_manager.total_memory == 2048
        assert memory_manager.get_free_memory() == 2048
        assert len(memory_manager.process_map) == 0


# ============================================
# Block Management Tests
# ============================================

class TestMemoryBlock:
    """Test MemoryBlock class"""
    
    def test_block_creation(self):
        """Test creating a memory block"""
        block = MemoryBlock(0, 128, is_free=True)
        assert block.start == 0
        assert block.size == 128
        assert block.end == 128
        assert block.is_free is True
    
    def test_block_to_dict(self):
        """Test converting block to dictionary"""
        block = MemoryBlock(100, 256, is_free=False, process_name="Test")
        block_dict = block.to_dict()
        
        assert block_dict["start"] == 100
        assert block_dict["size"] == 256
        assert block_dict["end"] == 356
        assert block_dict["is_free"] is False
        assert block_dict["process_name"] == "Test"
    
    def test_block_repr(self):
        """Test block string representation"""
        block = MemoryBlock(0, 128, is_free=True)
        repr_str = repr(block)
        assert "Block" in repr_str
        assert "128KB" in repr_str


# ============================================
# Performance Tests
# ============================================

class TestPerformance:
    """Test performance characteristics"""
    
    def test_large_memory_initialization(self):
        """Test initialization with large memory"""
        manager = ImprovisedMemoryManager(1024 * 1024)  # 1GB
        assert manager.total_memory == 1024 * 1024
    
    def test_many_allocations_performance(self, memory_manager):
        """Test performance with many allocations"""
        success_count = 0
        for i in range(50):
            success, _, _ = memory_manager.allocate(f"P{i}", 16, use_buddy=False)
            if success:
                success_count += 1
        
        assert success_count > 0
    
    def test_compaction_performance(self, memory_manager):
        """Test compaction with many blocks"""
        # Create fragmented memory
        for i in range(20):
            memory_manager.allocate(f"P{i}", 32, use_buddy=False)
        
        # Deallocate alternating blocks
        for i in range(0, 20, 2):
            memory_manager.deallocate(f"P{i}")
        
        # Compact should complete successfully
        success, msg, moved = memory_manager.compact()
        assert success is True


# ============================================
# Run Tests
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
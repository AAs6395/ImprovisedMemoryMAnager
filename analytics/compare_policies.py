"""
Memory Manager Analytics and Visualization
Compare allocation policies and visualize memory usage trends
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.buddy_allocator import ImprovisedMemoryManager


# ============================================
# Simulation Functions
# ============================================

def simulate_workload(manager: ImprovisedMemoryManager, operations: List[Tuple]) -> dict:
    """
    Simulate a workload on the memory manager
    
    Args:
        manager: ImprovisedMemoryManager instance
        operations: List of (operation, process_name, size) tuples
        
    Returns:
        Dictionary with simulation statistics
    """
    stats = {
        'used_memory': [],
        'free_memory': [],
        'fragmentation': [],
        'blocks_count': [],
        'operations': [],
        'failed_allocations': 0,
        'successful_allocations': 0,
        'deallocations': 0,
        'compactions': 0
    }
    
    for i, operation in enumerate(operations):
        op_type = operation[0]
        
        if op_type == 'allocate':
            process_name, size = operation[1], operation[2]
            success, msg, addr = manager.allocate(process_name, size)
            
            if success:
                stats['successful_allocations'] += 1
            else:
                stats['failed_allocations'] += 1
        
        elif op_type == 'deallocate':
            process_name = operation[1]
            success, msg = manager.deallocate(process_name)
            
            if success:
                stats['deallocations'] += 1
        
        elif op_type == 'compact':
            success, msg, moved = manager.compact()
            if success:
                stats['compactions'] += 1
        
        # Record current state
        stats['used_memory'].append(manager.get_used_memory())
        stats['free_memory'].append(manager.get_free_memory())
        stats['fragmentation'].append(manager.get_fragmentation_ratio() * 100)
        stats['blocks_count'].append(len(manager.blocks))
        stats['operations'].append(i)
    
    return stats


def generate_random_workload(num_operations: int = 100) -> List[Tuple]:
    """
    Generate a random workload for testing
    
    Args:
        num_operations: Number of operations to generate
        
    Returns:
        List of operations
    """
    operations = []
    active_processes = []
    
    for i in range(num_operations):
        # 60% allocate, 30% deallocate, 10% compact
        rand = np.random.random()
        
        if rand < 0.6 or len(active_processes) == 0:
            # Allocate
            process_name = f"P{i}"
            size = np.random.choice([32, 64, 128, 256, 512])
            operations.append(('allocate', process_name, size))
            active_processes.append(process_name)
        
        elif rand < 0.9 and len(active_processes) > 0:
            # Deallocate
            process_name = np.random.choice(active_processes)
            operations.append(('deallocate', process_name, None))
            active_processes.remove(process_name)
        
        else:
            # Compact
            operations.append(('compact', None, None))
    
    return operations


# ============================================
# Visualization Functions
# ============================================

def plot_memory_usage_over_time(stats: dict, title: str = "Memory Usage Over Time"):
    """
    Plot memory usage trends
    
    Args:
        stats: Statistics dictionary from simulation
        title: Plot title
    """
    plt.figure(figsize=(14, 8))
    
    # Plot 1: Used vs Free Memory
    plt.subplot(2, 2, 1)
    plt.plot(stats['operations'], stats['used_memory'], 
             label='Used Memory', color='#ef4444', linewidth=2)
    plt.plot(stats['operations'], stats['free_memory'], 
             label='Free Memory', color='#10b981', linewidth=2)
    plt.xlabel('Operation Number')
    plt.ylabel('Memory (KB)')
    plt.title('Memory Usage Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Fragmentation
    plt.subplot(2, 2, 2)
    plt.plot(stats['operations'], stats['fragmentation'], 
             color='#f59e0b', linewidth=2)
    plt.xlabel('Operation Number')
    plt.ylabel('Fragmentation (%)')
    plt.title('Memory Fragmentation')
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Number of Blocks
    plt.subplot(2, 2, 3)
    plt.plot(stats['operations'], stats['blocks_count'], 
             color='#6366f1', linewidth=2)
    plt.xlabel('Operation Number')
    plt.ylabel('Number of Blocks')
    plt.title('Memory Block Count')
    plt.grid(True, alpha=0.3)
    
    # Plot 4: Operation Statistics
    plt.subplot(2, 2, 4)
    operations_data = [
        stats['successful_allocations'],
        stats['failed_allocations'],
        stats['deallocations'],
        stats['compactions']
    ]
    operations_labels = ['Successful\nAllocations', 'Failed\nAllocations', 
                        'Deallocations', 'Compactions']
    colors = ['#10b981', '#ef4444', '#f59e0b', '#6366f1']
    
    plt.bar(operations_labels, operations_data, color=colors)
    plt.ylabel('Count')
    plt.title('Operation Statistics')
    plt.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()


def plot_comparison(buddy_stats: dict, no_buddy_stats: dict):
    """
    Compare buddy system vs non-buddy allocation
    
    Args:
        buddy_stats: Statistics with buddy system
        no_buddy_stats: Statistics without buddy system
    """
    plt.figure(figsize=(14, 6))
    
    # Plot 1: Fragmentation Comparison
    plt.subplot(1, 2, 1)
    plt.plot(buddy_stats['operations'], buddy_stats['fragmentation'], 
             label='With Buddy System', color='#6366f1', linewidth=2)
    plt.plot(no_buddy_stats['operations'], no_buddy_stats['fragmentation'], 
             label='Without Buddy System', color='#ef4444', linewidth=2)
    plt.xlabel('Operation Number')
    plt.ylabel('Fragmentation (%)')
    plt.title('Fragmentation: Buddy vs Non-Buddy')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Success Rate Comparison
    plt.subplot(1, 2, 2)
    categories = ['With Buddy', 'Without Buddy']
    successful = [buddy_stats['successful_allocations'], 
                  no_buddy_stats['successful_allocations']]
    failed = [buddy_stats['failed_allocations'], 
              no_buddy_stats['failed_allocations']]
    
    x = np.arange(len(categories))
    width = 0.35
    
    plt.bar(x - width/2, successful, width, label='Successful', color='#10b981')
    plt.bar(x + width/2, failed, width, label='Failed', color='#ef4444')
    
    plt.xlabel('Allocation Strategy')
    plt.ylabel('Number of Allocations')
    plt.title('Allocation Success Rate')
    plt.xticks(x, categories)
    plt.legend()
    plt.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('Buddy System vs Non-Buddy Comparison', 
                 fontsize=16, fontweight='bold')
    plt.tight_layout()


def plot_memory_state_snapshot(manager: ImprovisedMemoryManager, title: str = "Memory State"):
    """
    Visualize current memory state as a bar chart
    
    Args:
        manager: ImprovisedMemoryManager instance
        title: Plot title
    """
    plt.figure(figsize=(12, 4))
    
    blocks = manager.blocks
    colors = []
    labels = []
    sizes = []
    
    for block in blocks:
        if block.is_free:
            colors.append('#94a3b8')
            labels.append(f'FREE\n{block.size}KB')
        else:
            colors.append('#6366f1')
            labels.append(f'{block.process_name}\n{block.size}KB')
        sizes.append(block.size)
    
    # Create horizontal bar
    left = 0
    for i, size in enumerate(sizes):
        plt.barh(0, size, left=left, height=0.5, 
                color=colors[i], edgecolor='white', linewidth=2)
        
        # Add label
        if size > 50:  # Only show label if block is large enough
            plt.text(left + size/2, 0, labels[i], 
                    ha='center', va='center', fontsize=8, fontweight='bold')
        
        left += size
    
    plt.xlim(0, manager.total_memory)
    plt.ylim(-0.5, 0.5)
    plt.xlabel('Memory Address (KB)')
    plt.title(title)
    plt.yticks([])
    plt.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()


# ============================================
# Analysis Functions
# ============================================

def analyze_performance(stats: dict) -> dict:
    """
    Analyze performance metrics from simulation
    
    Args:
        stats: Statistics dictionary
        
    Returns:
        Dictionary with performance metrics
    """
    total_ops = len(stats['operations'])
    
    metrics = {
        'average_used_memory': np.mean(stats['used_memory']),
        'average_free_memory': np.mean(stats['free_memory']),
        'average_fragmentation': np.mean(stats['fragmentation']),
        'max_fragmentation': np.max(stats['fragmentation']),
        'average_blocks': np.mean(stats['blocks_count']),
        'allocation_success_rate': (stats['successful_allocations'] / 
                                   (stats['successful_allocations'] + stats['failed_allocations']) * 100
                                   if (stats['successful_allocations'] + stats['failed_allocations']) > 0 else 0),
        'total_operations': total_ops,
        'successful_allocations': stats['successful_allocations'],
        'failed_allocations': stats['failed_allocations'],
        'deallocations': stats['deallocations'],
        'compactions': stats['compactions']
    }
    
    return metrics


def print_performance_report(metrics: dict, title: str = "Performance Report"):
    """
    Print formatted performance report
    
    Args:
        metrics: Performance metrics dictionary
        title: Report title
    """
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)
    print(f"\n📊 Memory Usage:")
    print(f"  • Average Used Memory:    {metrics['average_used_memory']:.2f} KB")
    print(f"  • Average Free Memory:    {metrics['average_free_memory']:.2f} KB")
    
    print(f"\n🔧 Fragmentation:")
    print(f"  • Average Fragmentation:  {metrics['average_fragmentation']:.2f}%")
    print(f"  • Maximum Fragmentation:  {metrics['max_fragmentation']:.2f}%")
    print(f"  • Average Block Count:    {metrics['average_blocks']:.2f}")
    
    print(f"\n✅ Operations:")
    print(f"  • Total Operations:       {metrics['total_operations']}")
    print(f"  • Successful Allocations: {metrics['successful_allocations']}")
    print(f"  • Failed Allocations:     {metrics['failed_allocations']}")
    print(f"  • Deallocations:          {metrics['deallocations']}")
    print(f"  • Compactions:            {metrics['compactions']}")
    print(f"  • Success Rate:           {metrics['allocation_success_rate']:.2f}%")
    print("="*60 + "\n")


# ============================================
# Main Execution
# ============================================

def main():
    """Main function to run analytics and comparisons"""
    print("\n" + "="*60)
    print("  IMPROVISED MEMORY MANAGER - ANALYTICS")
    print("="*60 + "\n")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate workload
    print("📝 Generating random workload...")
    operations = generate_random_workload(150)
    print(f"✅ Generated {len(operations)} operations\n")
    
    # Test 1: With Buddy System
    print("🔄 Running simulation with Buddy System...")
    manager_buddy = ImprovisedMemoryManager(2048)
    buddy_stats = simulate_workload(manager_buddy, operations)
    buddy_metrics = analyze_performance(buddy_stats)
    print_performance_report(buddy_metrics, "WITH BUDDY SYSTEM")
    
    # Test 2: Without Buddy System (modify allocate to not use buddy)
    print("🔄 Running simulation without Buddy System...")
    manager_no_buddy = ImprovisedMemoryManager(2048)
    # Modify operations to disable buddy
    operations_no_buddy = []
    for op in operations:
        if op[0] == 'allocate':
            operations_no_buddy.append(('allocate_no_buddy', op[1], op[2]))
        else:
            operations_no_buddy.append(op)
    
    # Custom simulation for no buddy
    no_buddy_stats = {
        'used_memory': [],
        'free_memory': [],
        'fragmentation': [],
        'blocks_count': [],
        'operations': [],
        'failed_allocations': 0,
        'successful_allocations': 0,
        'deallocations': 0,
        'compactions': 0
    }
    
    for i, operation in enumerate(operations_no_buddy):
        op_type = operation[0]
        
        if op_type == 'allocate_no_buddy':
            process_name, size = operation[1], operation[2]
            success, msg, addr = manager_no_buddy.allocate(process_name, size, use_buddy=False)
            
            if success:
                no_buddy_stats['successful_allocations'] += 1
            else:
                no_buddy_stats['failed_allocations'] += 1
        
        elif op_type == 'deallocate':
            process_name = operation[1]
            success, msg = manager_no_buddy.deallocate(process_name)
            
            if success:
                no_buddy_stats['deallocations'] += 1
        
        elif op_type == 'compact':
            success, msg, moved = manager_no_buddy.compact()
            if success:
                no_buddy_stats['compactions'] += 1
        
        no_buddy_stats['used_memory'].append(manager_no_buddy.get_used_memory())
        no_buddy_stats['free_memory'].append(manager_no_buddy.get_free_memory())
        no_buddy_stats['fragmentation'].append(manager_no_buddy.get_fragmentation_ratio() * 100)
        no_buddy_stats['blocks_count'].append(len(manager_no_buddy.blocks))
        no_buddy_stats['operations'].append(i)
    
    no_buddy_metrics = analyze_performance(no_buddy_stats)
    print_performance_report(no_buddy_metrics, "WITHOUT BUDDY SYSTEM")
    
    # Generate visualizations
    print("📈 Generating visualizations...")
    
    plot_memory_usage_over_time(buddy_stats, "Memory Manager Performance - WITH Buddy System")
    plt.savefig('analytics_buddy_system.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: analytics_buddy_system.png")
    
    plot_memory_usage_over_time(no_buddy_stats, "Memory Manager Performance - WITHOUT Buddy System")
    plt.savefig('analytics_no_buddy.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: analytics_no_buddy.png")
    
    plot_comparison(buddy_stats, no_buddy_stats)
    plt.savefig('analytics_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: analytics_comparison.png")
    
    plot_memory_state_snapshot(manager_buddy, "Memory State Snapshot - WITH Buddy System")
    plt.savefig('memory_state_buddy.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: memory_state_buddy.png")
    
    plot_memory_state_snapshot(manager_no_buddy, "Memory State Snapshot - WITHOUT Buddy System")
    plt.savefig('memory_state_no_buddy.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: memory_state_no_buddy.png")
    
    print("\n✨ All analytics complete! Check the generated PNG files.\n")
    plt.show()


if __name__ == "__main__":
    main()
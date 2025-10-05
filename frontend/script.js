// ============================================
// IMPROVISED MEMORY MANAGER - FRONTEND SCRIPT
// ============================================

const API_BASE_URL = 'http://localhost:8000';

// State management
let memoryState = {
    totalMemory: 0,
    usedMemory: 0,
    freeMemory: 0,
    blocks: [],
    processes: []
};

// DOM Elements
const elements = {
    totalMemory: document.getElementById('totalMemory'),
    initMemory: document.getElementById('initMemory'),
    processName: document.getElementById('processName'),
    processSize: document.getElementById('processSize'),
    allocateBtn: document.getElementById('allocateBtn'),
    compactBtn: document.getElementById('compactBtn'),
    clearLog: document.getElementById('clearLog'),
    memoryBlocks: document.getElementById('memoryBlocks'),
    processList: document.getElementById('processList'),
    activityLog: document.getElementById('activityLog'),
    statTotal: document.getElementById('statTotal'),
    statUsed: document.getElementById('statUsed'),
    statFree: document.getElementById('statFree'),
    statFrag: document.getElementById('statFrag'),
    statUsedPercent: document.getElementById('statUsedPercent'),
    statFreePercent: document.getElementById('statFreePercent'),
    fragBlocks: document.getElementById('fragBlocks'),
    memoryBarFill: document.getElementById('memoryBarFill'),
    serverStatus: document.getElementById('serverStatus')
};

// ============================================
// API FUNCTIONS
// ============================================

async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'API request failed');
        }

        updateServerStatus(true);
        return data;
    } catch (error) {
        updateServerStatus(false);
        throw error;
    }
}

function updateServerStatus(connected) {
    if (connected) {
        elements.serverStatus.textContent = '🟢 Connected';
        elements.serverStatus.style.color = '#10b981';
    } else {
        elements.serverStatus.textContent = '🔴 Disconnected';
        elements.serverStatus.style.color = '#ef4444';
    }
}

// ============================================
// MEMORY OPERATIONS
// ============================================

async function initializeMemory() {
    const size = parseInt(elements.totalMemory.value);

    if (!size || size < 64) {
        addLog('Please enter a valid memory size (minimum 64 KB)', 'error');
        return;
    }

    try {
        const data = await apiCall('/initialize', 'POST', { total_memory: size });
        
        memoryState = {
            totalMemory: size,
            usedMemory: 0,
            freeMemory: size,
            blocks: data.blocks || [],
            processes: []
        };

        updateUI();
        addLog(`Memory initialized with ${size} KB`, 'success');
    } catch (error) {
        addLog(`Failed to initialize memory: ${error.message}`, 'error');
    }
}

async function allocateProcess() {
    const name = elements.processName.value.trim();
    const size = parseInt(elements.processSize.value);

    if (!name) {
        addLog('Please enter a process name', 'error');
        return;
    }

    if (!size || size < 1) {
        addLog('Please enter a valid process size', 'error');
        return;
    }

    if (memoryState.totalMemory === 0) {
        addLog('Please initialize memory first', 'error');
        return;
    }

    try {
        const data = await apiCall('/allocate', 'POST', {
            process_name: name,
            size: size
        });

        if (data.success) {
            memoryState.blocks = data.blocks;
            memoryState.usedMemory = data.used_memory;
            memoryState.freeMemory = data.free_memory;
            
            // Add to processes list
            memoryState.processes.push({
                name: name,
                size: size,
                start_address: data.start_address
            });

            updateUI();
            addLog(`✅ Process "${name}" (${size} KB) allocated at address ${data.start_address}`, 'success');
            
            // Clear input fields
            elements.processName.value = '';
            elements.processSize.value = '';
        } else {
            addLog(`❌ Failed to allocate "${name}": ${data.message}`, 'error');
        }
    } catch (error) {
        addLog(`Failed to allocate process: ${error.message}`, 'error');
    }
}

async function deallocateProcess(processName) {
    try {
        const data = await apiCall('/deallocate', 'POST', {
            process_name: processName
        });

        if (data.success) {
            memoryState.blocks = data.blocks;
            memoryState.usedMemory = data.used_memory;
            memoryState.freeMemory = data.free_memory;
            memoryState.processes = memoryState.processes.filter(p => p.name !== processName);

            updateUI();
            addLog(`🗑️ Process "${processName}" deallocated`, 'info');
        } else {
            addLog(`Failed to deallocate "${processName}": ${data.message}`, 'error');
        }
    } catch (error) {
        addLog(`Failed to deallocate process: ${error.message}`, 'error');
    }
}

async function compactMemory() {
    if (memoryState.totalMemory === 0) {
        addLog('Please initialize memory first', 'error');
        return;
    }

    try {
        const data = await apiCall('/compact', 'POST');

        if (data.success) {
            memoryState.blocks = data.blocks;
            
            updateUI();
            addLog(`🔄 Memory compacted successfully. Moved ${data.moved_processes || 0} processes`, 'warning');
        } else {
            addLog(`Compaction failed: ${data.message}`, 'error');
        }
    } catch (error) {
        addLog(`Failed to compact memory: ${error.message}`, 'error');
    }
}

async function getMemoryStatus() {
    try {
        const data = await apiCall('/status');
        
        memoryState.totalMemory = data.total_memory;
        memoryState.usedMemory = data.used_memory;
        memoryState.freeMemory = data.free_memory;
        memoryState.blocks = data.blocks;
        
        updateUI();
    } catch (error) {
        console.error('Failed to get memory status:', error);
    }
}

// ============================================
// UI UPDATE FUNCTIONS
// ============================================

function updateUI() {
    updateStats();
    updateMemoryVisualization();
    updateProcessList();
}

function updateStats() {
    const { totalMemory, usedMemory, freeMemory, blocks } = memoryState;
    
    elements.statTotal.textContent = `${totalMemory} KB`;
    elements.statUsed.textContent = `${usedMemory} KB`;
    elements.statFree.textContent = `${freeMemory} KB`;
    
    const usedPercent = totalMemory > 0 ? ((usedMemory / totalMemory) * 100).toFixed(1) : 0;
    const freePercent = totalMemory > 0 ? ((freeMemory / totalMemory) * 100).toFixed(1) : 0;
    
    elements.statUsedPercent.textContent = `${usedPercent}%`;
    elements.statFreePercent.textContent = `${freePercent}%`;
    
    // Calculate fragmentation
    const freeBlocks = blocks.filter(b => b.is_free).length;
    const fragmentation = freeBlocks > 1 ? ((freeBlocks - 1) / blocks.length * 100).toFixed(1) : 0;
    
    elements.statFrag.textContent = `${fragmentation}%`;
    elements.fragBlocks.textContent = `${freeBlocks} free blocks`;
    
    // Update memory bar
    elements.memoryBarFill.style.width = `${usedPercent}%`;
    elements.memoryBarFill.textContent = `${usedPercent}% Used`;
}

function updateMemoryVisualization() {
    const { blocks, totalMemory } = memoryState;
    
    if (blocks.length === 0) {
        elements.memoryBlocks.innerHTML = '<div class="empty-state"><p>Initialize memory to start visualization</p></div>';
        return;
    }
    
    elements.memoryBlocks.innerHTML = '';
    
    blocks.forEach(block => {
        const blockDiv = document.createElement('div');
        blockDiv.className = `memory-block ${block.is_free ? 'free' : 'allocated'}`;
        
        // Calculate width based on size
        const widthPercent = (block.size / totalMemory) * 100;
        blockDiv.style.minWidth = `${Math.max(widthPercent, 10)}%`;
        
        blockDiv.innerHTML = `
            <div class="block-info">
                <span class="block-name">${block.is_free ? 'FREE' : block.process_name}</span>
                <span class="block-size">${block.size} KB</span>
                <span class="block-address">0x${block.start.toString(16).toUpperCase()}</span>
            </div>
        `;
        
        elements.memoryBlocks.appendChild(blockDiv);
    });
}

function updateProcessList() {
    const { processes } = memoryState;
    
    if (processes.length === 0) {
        elements.processList.innerHTML = '<div class="empty-state">No active processes</div>';
        return;
    }
    
    elements.processList.innerHTML = '';
    
    processes.forEach(process => {
        const processDiv = document.createElement('div');
        processDiv.className = 'process-item';
        
        processDiv.innerHTML = `
            <div class="process-info">
                <div class="process-detail">
                    <strong>Process Name</strong>
                    <span>${process.name}</span>
                </div>
                <div class="process-detail">
                    <strong>Size</strong>
                    <span>${process.size} KB</span>
                </div>
                <div class="process-detail">
                    <strong>Start Address</strong>
                    <span>0x${process.start_address.toString(16).toUpperCase()}</span>
                </div>
            </div>
            <button class="deallocate-btn" onclick="deallocateProcess('${process.name}')">
                🗑️ Deallocate
            </button>
        `;
        
        elements.processList.appendChild(processDiv);
    });
}

function addLog(message, type = 'info') {
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    
    const time = new Date().toLocaleTimeString();
    logEntry.innerHTML = `
        ${message}
        <span class="log-time">${time}</span>
    `;
    
    elements.activityLog.insertBefore(logEntry, elements.activityLog.firstChild);
    
    // Limit log entries to 50
    while (elements.activityLog.children.length > 50) {
        elements.activityLog.removeChild(elements.activityLog.lastChild);
    }
}

function clearLog() {
    elements.activityLog.innerHTML = '';
    addLog('Activity log cleared', 'info');
}

// ============================================
// EVENT LISTENERS
// ============================================

elements.initMemory.addEventListener('click', initializeMemory);
elements.allocateBtn.addEventListener('click', allocateProcess);
elements.compactBtn.addEventListener('click', compactMemory);
elements.clearLog.addEventListener('click', clearLog);

// Enter key support
elements.processSize.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        allocateProcess();
    }
});

elements.totalMemory.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        initializeMemory();
    }
});

// ============================================
// INITIALIZATION
// ============================================

// Check server status on load
window.addEventListener('load', () => {
    addLog('Memory Manager UI loaded', 'info');
    addLog('Initialize memory to begin', 'info');
    
    // Try to connect to server
    apiCall('/status').catch(() => {
        addLog('⚠️ Backend server not connected. Please start the FastAPI server.', 'warning');
    });
});

// Periodic status check (every 10 seconds)
setInterval(() => {
    if (memoryState.totalMemory > 0) {
        getMemoryStatus();
    }
}, 10000);

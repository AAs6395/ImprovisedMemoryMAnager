// ================================================================
//  MEMOS – Improvised Memory Manager · Frontend Script
// ================================================================

const API = 'http://localhost:8000';

// ── State ──────────────────────────────────────────────────────
let state = {
  totalMemory: 0,
  usedMemory: 0,
  freeMemory: 0,
  blocks: [],
  processList: [],
  fragmentation: 0,
  initialized: false,
};

// ── DOM helpers ────────────────────────────────────────────────
const $ = id => document.getElementById(id);

// ── Navigation ────────────────────────────────────────────────
document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.panel;
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    $(`panel-${target}`).classList.add('active');
  });
});

// ── Connection status ──────────────────────────────────────────
function setConn(online) {
  const dot = $('connDot');
  const lbl = $('connLabel');
  if (online) {
    dot.className = 'conn-dot online';
    lbl.textContent = 'Connected';
  } else {
    dot.className = 'conn-dot offline';
    lbl.textContent = 'Offline';
  }
}

// ── API call ───────────────────────────────────────────────────
async function api(endpoint, method = 'GET', body = null) {
  try {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(API + endpoint, opts);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Request failed');
    setConn(true);
    return data;
  } catch (e) {
    setConn(false);
    throw e;
  }
}

// ── Toast ──────────────────────────────────────────────────────
function toast(msg, type = 'info') {
  const icons = { ok: '✓', err: '✕', warn: '⚠', info: 'ℹ' };
  const wrap = $('toastWrap');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span class="toast-icon">${icons[type] || 'ℹ'}</span><span>${msg}</span>`;
  wrap.appendChild(el);
  setTimeout(() => {
    el.style.transition = 'opacity .3s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 300);
  }, 3200);
}

// ── Log ────────────────────────────────────────────────────────
const LOG_TYPES = { ok: 'ok', err: 'err', warn: 'warn', info: 'info' };

function addLog(msg, type = 'info') {
  const wrap = $('logWrap');
  // Remove empty placeholder
  const emp = wrap.querySelector('.log-empty');
  if (emp) emp.remove();

  const now = new Date();
  const t = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}:${now.getSeconds().toString().padStart(2,'0')}`;
  const labels = { ok: 'SUCCESS', err: 'ERROR', warn: 'WARN', info: 'INFO' };

  const el = document.createElement('div');
  el.className = 'log-entry';
  el.innerHTML = `
    <span class="log-time">${t}</span>
    <span class="log-badge ${type}">${labels[type] || 'INFO'}</span>
    <span class="log-msg">${msg}</span>`;
  wrap.insertBefore(el, wrap.firstChild);

  // Limit to 200 entries
  while (wrap.children.length > 200) wrap.removeChild(wrap.lastChild);
}

$('clearLogBtn').addEventListener('click', () => {
  $('logWrap').innerHTML = '<div class="log-empty">Log cleared</div>';
  addLog('Activity log cleared', 'info');
});

// ── Apply state to UI ──────────────────────────────────────────
function applyState(data) {
  state.totalMemory   = data.total_memory   ?? state.totalMemory;
  state.usedMemory    = data.used_memory    ?? state.usedMemory;
  state.freeMemory    = data.free_memory    ?? state.freeMemory;
  state.blocks        = data.blocks         ?? state.blocks;
  state.processList   = data.process_list   ?? state.processList;
  state.fragmentation = data.fragmentation  ?? state.fragmentation;
  state.initialized   = data.initialized !== false;
  renderAll();
}

function renderAll() {
  renderKPIs();
  renderMemoryMap();
  renderUsageBar();
  renderProcessTable();
}

// ── KPIs ────────────────────────────────────────────────────────
function renderKPIs() {
  const { totalMemory, usedMemory, freeMemory, fragmentation, blocks } = state;
  const usedPct = totalMemory ? (usedMemory / totalMemory * 100).toFixed(1) : 0;
  const freePct = totalMemory ? (freeMemory / totalMemory * 100).toFixed(1) : 0;
  const freeBlocks = blocks.filter(b => b.is_free).length;

  $('kpiTotal').textContent = totalMemory ? `${totalMemory} KB` : '— KB';
  $('kpiUsed').textContent  = totalMemory ? `${usedMemory} KB` : '— KB';
  $('kpiFree').textContent  = totalMemory ? `${freeMemory} KB` : '— KB';
  $('kpiFrag').textContent  = totalMemory ? `${fragmentation}%` : '—%';

  $('kpiUsedPct').textContent   = totalMemory ? `${usedPct}% of total` : '—';
  $('kpiFreePct').textContent   = totalMemory ? `${freePct}% of total` : '—';
  $('kpiFragBlocks').textContent = totalMemory ? `${freeBlocks} free block${freeBlocks !== 1 ? 's' : ''}` : '—';
  $('kpiTotalBar').style.width  = '100%';
}

// ── Memory Map ────────────────────────────────────────────────
function renderMemoryMap() {
  const map = $('memMap');
  const ruler = $('memRuler');
  map.innerHTML = '';
  ruler.innerHTML = '';

  const { blocks, totalMemory } = state;
  if (!totalMemory || !blocks.length) {
    map.innerHTML = '<div class="mem-empty">Initialize memory to see the map</div>';
    return;
  }

  // Palette for different processes
  const palette = [
    '#3b82f6','#8b5cf6','#06b6d4','#10b981','#f59e0b','#ef4444','#ec4899','#14b8a6',
  ];
  const procColors = {};
  let colorIdx = 0;

  blocks.forEach(block => {
    const pct = (block.size / totalMemory) * 100;
    const el = document.createElement('div');
    el.className = `mem-block ${block.is_free ? 'free' : 'alloc'}`;
    el.style.width = `${Math.max(pct, 1.5)}%`;

    if (!block.is_free) {
      if (!procColors[block.process_name]) {
        procColors[block.process_name] = palette[colorIdx++ % palette.length];
      }
      const c = procColors[block.process_name];
      el.style.setProperty('--accent-local', c);
      el.style.borderTopColor = c;
      el.style.background = `linear-gradient(180deg, ${c}33 0%, ${c}15 100%)`;
      el.style.color = c;
    }

    el.innerHTML = `
      <span class="mb-name">${block.is_free ? 'FREE' : block.process_name}</span>
      ${pct > 4 ? `<span class="mb-size">${block.size}KB</span>` : ''}`;

    el.title = `${block.is_free ? 'Free' : block.process_name} | ${block.size} KB | 0x${block.start.toString(16).toUpperCase()}–0x${block.end.toString(16).toUpperCase()}`;
    map.appendChild(el);
  });

  // Ruler ticks every 25%
  [0, 25, 50, 75, 100].forEach(pct => {
    const tick = document.createElement('span');
    tick.className = 'ruler-tick';
    tick.style.left = `${pct}%`;
    tick.textContent = `${Math.round(totalMemory * pct / 100)} KB`;
    ruler.appendChild(tick);
  });
}

// ── Usage bar ─────────────────────────────────────────────────
function renderUsageBar() {
  const { totalMemory, usedMemory } = state;
  const pct = totalMemory ? (usedMemory / totalMemory * 100).toFixed(1) : 0;
  $('usageBar').style.width = `${pct}%`;
  $('usageBarLabel').textContent = pct > 8 ? `${pct}% used` : '';
}

// ── Process Table ─────────────────────────────────────────────
function renderProcessTable() {
  const tbody = $('procTableBody');
  const { processList, totalMemory } = state;

  $('procCountBadge').textContent = processList.length;

  if (!processList.length) {
    tbody.innerHTML = '<tr class="empty-row"><td colspan="6">No active processes</td></tr>';
    return;
  }

  tbody.innerHTML = processList.map(p => {
    const pct = totalMemory ? (p.size / totalMemory * 100).toFixed(1) : 0;
    return `
      <tr>
        <td><div class="proc-name-cell"><span class="proc-dot"></span>${escHtml(p.name)}</div></td>
        <td>${p.size} KB</td>
        <td>0x${p.start.toString(16).toUpperCase()}</td>
        <td>0x${p.end.toString(16).toUpperCase()}</td>
        <td class="pct-bar-cell">
          <div class="pct-bar-track">
            <div class="pct-bar-fill" style="width:${pct}%"></div>
          </div>
          <span style="font-size:10.5px;color:var(--text2)">${pct}%</span>
        </td>
        <td>
          <button class="btn btn-danger btn-sm" onclick="deallocate('${escHtml(p.name)}')">Free</button>
        </td>
      </tr>`;
  }).join('');
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Alloc preview ──────────────────────────────────────────────
function updateAllocPreview() {
  const name = $('procName').value.trim();
  const size = parseInt($('procSize').value);
  const buddy = $('useBuddy').checked;
  const hint = $('buddyHint');
  hint.textContent = buddy ? 'ON – sizes rounded to next power of 2' : 'OFF – exact size used';

  const preview = $('allocPreview');
  if (!name && !size) { preview.textContent = 'Fill in the form above to see a preview'; return; }

  let actual = size;
  if (buddy && size > 0) {
    actual = Math.pow(2, Math.ceil(Math.log2(size)));
  }
  const parts = [];
  if (name) parts.push(`Process: ${name}`);
  if (size > 0) {
    parts.push(`Requested: ${size} KB`);
    if (buddy && actual !== size) parts.push(`Allocated: ${actual} KB (buddy rounded)`);
    else if (size > 0) parts.push(`Allocated: ${actual} KB`);
  }
  if (state.totalMemory && actual > 0) {
    const fits = actual <= state.freeMemory;
    parts.push(fits ? `✓ Fits in free memory (${state.freeMemory} KB available)` : `✗ Insufficient free memory (${state.freeMemory} KB available)`);
  }
  preview.textContent = parts.join(' · ');
}

$('procName').addEventListener('input', updateAllocPreview);
$('procSize').addEventListener('input', updateAllocPreview);
$('useBuddy').addEventListener('change', updateAllocPreview);

// ── Operations ────────────────────────────────────────────────

// Initialize
$('initBtn').addEventListener('click', async () => {
  const size = parseInt($('memSizeInput').value);
  if (!size || size < 1) { toast('Enter a valid memory size', 'err'); return; }
  try {
    const data = await api('/initialize', 'POST', { total_memory: size });
    applyState(data);
    addLog(`Memory initialized with ${size} KB`, 'ok');
    toast(`Memory initialized: ${size} KB`, 'ok');
  } catch (e) {
    addLog(`Init failed: ${e.message}`, 'err');
    toast(e.message, 'err');
  }
});

// Allocate
$('allocBtn').addEventListener('click', async () => {
  const name = $('procName').value.trim();
  const size = parseInt($('procSize').value);
  const buddy = $('useBuddy').checked;

  if (!name) { toast('Process name required', 'warn'); return; }
  if (!size || size < 1) { toast('Valid size required', 'warn'); return; }
  if (!state.initialized) { toast('Initialize memory first', 'warn'); return; }

  try {
    const data = await api('/allocate', 'POST', { process_name: name, size, use_buddy: buddy });
    applyState(data);
    if (data.success) {
      addLog(`Allocated: ${name} (${data.used_memory - (state.usedMemory - data.used_memory + data.used_memory)}→ addr 0x${(data.start_address||0).toString(16).toUpperCase()}) – ${data.message}`, 'ok');
      addLog(data.message, 'ok');
      toast(data.message, 'ok');
      $('procName').value = '';
      $('procSize').value = '';
      updateAllocPreview();
    } else {
      addLog(`Allocate failed: ${data.message}`, 'err');
      toast(data.message, 'err');
    }
  } catch (e) {
    addLog(`Allocate error: ${e.message}`, 'err');
    toast(e.message, 'err');
  }
});

// Enter key in alloc panel
$('procSize').addEventListener('keypress', e => { if (e.key === 'Enter') $('allocBtn').click(); });

// Deallocate (called from table)
async function deallocate(name) {
  try {
    const data = await api('/deallocate', 'POST', { process_name: name });
    applyState(data);
    if (data.success) {
      addLog(`Freed: ${name}`, 'ok');
      toast(`Process "${name}" freed`, 'ok');
    } else {
      addLog(`Dealloc failed: ${data.message}`, 'err');
      toast(data.message, 'err');
    }
  } catch (e) {
    addLog(`Dealloc error: ${e.message}`, 'err');
    toast(e.message, 'err');
  }
}

// Compact
$('compactBtn').addEventListener('click', async () => {
  if (!state.initialized) { toast('Initialize memory first', 'warn'); return; }
  try {
    const data = await api('/compact', 'POST');
    applyState(data);
    if (data.success) {
      addLog(`Compacted: ${data.moved_processes} block(s) relocated. ${data.message}`, 'warn');
      toast(`Compaction complete – ${data.moved_processes} block(s) moved`, 'warn');
    } else {
      addLog(`Compact: ${data.message}`, 'info');
      toast(data.message, 'info');
    }
  } catch (e) {
    addLog(`Compact error: ${e.message}`, 'err');
    toast(e.message, 'err');
  }
});

// Reset
$('resetBtn').addEventListener('click', async () => {
  if (!state.initialized) { toast('Nothing to reset', 'warn'); return; }
  if (!confirm('Reset all memory? All processes will be lost.')) return;
  try {
    const data = await api('/reset', 'POST');
    applyState(data);
    addLog('Memory reset', 'warn');
    toast('Memory reset', 'warn');
  } catch (e) {
    addLog(`Reset error: ${e.message}`, 'err');
    toast(e.message, 'err');
  }
});

// ── Periodic refresh ──────────────────────────────────────────
async function refreshStatus() {
  if (!state.initialized) return;
  try {
    const data = await api('/status');
    applyState(data);
  } catch (_) {}
}
setInterval(refreshStatus, 8000);

// ── Boot ──────────────────────────────────────────────────────
(async () => {
  addLog('Memory Manager UI loaded', 'info');
  try {
    const data = await api('/status');
    applyState(data);
    if (data.initialized) {
      addLog('Reconnected to existing session', 'ok');
      toast('Reconnected to server', 'ok');
    } else {
      addLog('Backend connected. Initialize memory to begin.', 'info');
      toast('Backend connected', 'info');
    }
  } catch (_) {
    addLog('Backend not reachable. Start the FastAPI server.', 'err');
    toast('Backend not connected – start api.py', 'err');
    $('logWrap').innerHTML = '<div class="log-empty">Start the server with: python backend/api.py</div>';
  }
})();

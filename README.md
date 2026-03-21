# 💾 Improvised Memory Manager · v2.0

A full-stack memory management simulator combining **Best-Fit allocation**, **Buddy System rounding**, and **Memory Compaction** — with a modern dark terminal UI and a FastAPI REST backend.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the backend
cd backend
python api.py
# → Server at http://localhost:8000

# 3. Open the frontend
# Navigate to http://localhost:8000
# (or open frontend/index.html directly in a browser)
```

---

## Project Structure

```
improvised-memory-manager/
├── backend/
│   ├── buddy_allocator.py   # Core memory manager logic
│   └── api.py               # FastAPI REST API
├── frontend/
│   ├── index.html           # Single-page app
│   ├── styles.css           # Industrial terminal design
│   └── script.js            # State management + API calls
├── tests/
│   └── test_buddy.py        # 30+ pytest test cases
├── analytics/
│   └── compare_policies.py  # Performance comparison tool
├── requirements.txt
└── README.md
```

---

## API Reference

| Method | Endpoint     | Description                      |
|--------|--------------|----------------------------------|
| POST   | /initialize  | Initialize with total_memory KB  |
| POST   | /allocate    | Allocate memory (+ buddy option) |
| POST   | /deallocate  | Free a process's memory          |
| POST   | /compact     | Compact fragmented memory        |
| GET    | /status      | Get current memory state         |
| POST   | /reset       | Reset the memory manager         |
| GET    | /health      | Health check                     |
| GET    | /docs        | Swagger interactive docs         |

---

## Running Tests

```bash
cd improvised-memory-manager
pytest tests/test_buddy.py -v
```

## Analytics

```bash
cd analytics
python compare_policies.py
# Generates 5 PNG charts comparing buddy vs non-buddy allocation
```

---

## Algorithm Details

1. **Best-Fit** – Scans all free blocks, picks the smallest block that fits the request, minimizing wasted space.
2. **Buddy Rounding** – Optionally rounds the requested size up to the nearest power of 2 (e.g. 100 KB → 128 KB), reducing internal fragmentation over many allocations.
3. **Block Splitting** – If the chosen free block is larger than needed, the leftover is split into a new free block.
4. **Coalescing** – After every deallocation, adjacent free blocks are merged automatically.
5. **Compaction** – On demand (or automatically on allocation failure), all allocated blocks are moved to the front of memory, consolidating all free space into a single contiguous block.
6. **Auto-compact Fallback** – When no free block fits a request, compaction is attempted automatically before returning a failure.

---

## Tech Stack

| Layer     | Technology                 |
|-----------|----------------------------|
| Backend   | Python 3.8+, FastAPI, Uvicorn, Pydantic |
| Frontend  | Vanilla HTML/CSS/JS, Fetch API |
| Testing   | pytest, pytest-cov          |
| Analytics | matplotlib, numpy           |
| Fonts     | JetBrains Mono, Syne        |

---

## Bugs Fixed in v2.0

- `_merge_free_blocks`: previous version mutated the block being iterated; now rebuilds the list correctly.
- `get_fragmentation_ratio`: changed from counting free blocks to a meaningful metric (1 − largest_free / total_free).
- `deallocate`: comparison now uses both object identity and address to handle blocks rebuilt after compaction.
- `allocate`: validates empty process names, zero/negative sizes, and adds auto-compact fallback.
- Test imports: fixed `sys.path` so tests can be run from any directory.
- API: `process_list` is now returned in every status response so the frontend can track processes without maintaining separate state.

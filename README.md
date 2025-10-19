# 💾 Improvised Memory Manager

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Uniqueness](#uniqueness-of-the-project)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Analytics](#analytics)
- [Future Scope](#future-scope)
- [References](#references)

---

## 1. Project Overview

The **Improvised Memory Manager** is a comprehensive project designed to simulate and manage memory allocation in an operating system. It combines **Best-Fit allocation** with **compaction** and a **buddy system style hybrid** to efficiently allocate and deallocate memory for processes while minimizing fragmentation.

### Key Components:
- **Frontend UI**: Interactive web interface for real-time memory visualization
- **Python Backend**: FastAPI-based REST API for memory operations
- **Automated Tests**: Comprehensive test suite using pytest
- **Analytics Module**: Performance analysis and visualization tools

---

## 2. Problem Statement

Memory fragmentation and inefficient allocation are major issues in operating systems that can lead to:
- **Wasted memory resources**
- **Poor system performance**
- **Failed allocations despite available memory**
- **Increased overhead from fragmented blocks**

### Our Solution

This project addresses these challenges by implementing an **improvised memory manager** that:

1. ✅ Allocates memory to processes efficiently using a **best-fit approach**
2. ✅ Compacts memory when allocation fails due to fragmentation
3. ✅ Uses **buddy system style allocation** for faster allocation and reduced fragmentation
4. ✅ Visualizes memory usage in real-time for better understanding
5. ✅ Provides detailed analytics and performance metrics

---

## 3. Uniqueness of the Project

### What Makes This Different?

- **🔀 Hybrid Approach**: Combines best-fit allocation with buddy system principles for optimal performance
- **📊 Real-time Visualization**: Dynamic memory block visualization with color-coded states
- **🔄 Smart Compaction**: Automatic memory reorganization when fragmentation occurs
- **📈 Comprehensive Analytics**: Detailed performance metrics and comparison tools
- **🎨 Modern UI**: Beautiful, responsive interface with dark theme
- **🧪 Well-Tested**: Extensive test coverage with 30+ test cases
- **🚀 Production-Ready**: RESTful API with proper error handling and validation
- **👥 Team-Oriented**: Modular design allowing independent development

---

## 4. Features

### Core Features
✨ **Memory Initialization** - Set custom total memory size  
✨ **Process Allocation** - Allocate memory with best-fit algorithm  
✨ **Process Deallocation** - Free memory and merge adjacent blocks  
✨ **Memory Compaction** - Reorganize memory to reduce fragmentation  
✨ **Real-time Statistics** - Monitor usage, fragmentation, and performance  
✨ **Visual Representation** - Color-coded memory blocks display  
✨ **Activity Logging** - Track all operations with timestamps  

### Advanced Features
🔧 **Buddy System Option** - Toggle power-of-2 size rounding  
🔧 **Fragmentation Analysis** - Calculate and display fragmentation ratio  
🔧 **Auto-merge Blocks** - Automatically merge adjacent free blocks  
🔧 **Process Management** - View and manage all active processes  
🔧 **Error Handling** - Graceful error messages and validation  

---

## 5. Technology Stack

### Frontend
- **HTML5** - Structure and semantic markup
- **CSS3** - Modern styling with gradients and animations
- **JavaScript (ES6+)** - Dynamic UI updates and API communication
- **Fetch API** - HTTP requests to backend

### Backend
- **Python 3.8+** - Core programming language
- **FastAPI** - Modern web framework for building APIs
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server for FastAPI

### Testing & Analytics
- **pytest** - Testing framework
- **matplotlib** - Data visualization
- **numpy** - Numerical computations

---

## 6. Project Structure

```
improvised-memory-manager/
│
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── styles.css          # Styling and animations
│   └── script.js           # Frontend logic
│
├── backend/
│   ├── buddy_allocator.py  # Core memory manager logic
│   └── api.py              # FastAPI REST API
│
├── tests/
│   └── test_buddy.py       # Comprehensive test suite
│
├── analytics/
│   └── compare_policies.py # Performance analysis tools
│
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

---

## 7. Installation

### Prerequisites
- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/improvised-memory-manager.git
cd improvised-memory-manager
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation
```bash
python backend/buddy_allocator.py
```

If you see the demo output, installation is successful! ✅

---

## 8. Usage

### Starting the Backend Server

```bash
# Navigate to backend directory
cd backend

# Start the FastAPI server
python api.py

# Alternative: Use uvicorn directly
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
🚀 Starting Improvised Memory Manager API Server
📡 Server running at: http://localhost:8000
📚 API Documentation: http://localhost:8000/docs
```

### Starting the Frontend

```bash
# Open frontend/index.html in your browser
# Or use a simple HTTP server:
cd frontend
python -m http.server 8080
```

Then navigate to: `http://localhost:8080`

### Using the Application

1. **Initialize Memory**
   - Enter total memory size (e.g., 1024 KB)
   - Click "Initialize Memory"

2. **Allocate Processes**
   - Enter process name (e.g., "Chrome")
   - Enter size (e.g., 256 KB)
   - Click "Allocate Process"

3. **Deallocate Processes**
   - Click the "🗑️ Deallocate" button next to any active process

4. **Compact Memory**
   - Click "Compact Memory" to reorganize memory blocks

5. **Monitor Statistics**
   - View real-time stats in the dashboard
   - Check activity log for operation history

---

## 9. API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Initialize Memory
```http
POST /initialize
Content-Type: application/json

{
  "total_memory": 1024
}
```

#### 2. Allocate Process
```http
POST /allocate
Content-Type: application/json

{
  "process_name": "Chrome",
  "size": 256,
  "use_buddy": true
}
```

#### 3. Deallocate Process
```http
POST /deallocate
Content-Type: application/json

{
  "process_name": "Chrome"
}
```

#### 4. Compact Memory
```http
POST /compact
```

#### 5. Get Status
```http
GET /status
```

#### 6. Reset Memory
```http
POST /reset?total_memory=2048
```

### Interactive API Documentation
Visit `http://localhost:8000/docs` for Swagger UI documentation with interactive testing.

---

## 10. Testing

### Run All Tests
```bash
# Run all tests with verbose output
pytest tests/test_buddy.py -v

# Run with coverage report
pytest tests/test_buddy.py --cov=backend --cov-report=html

# Run specific test class
pytest tests/test_buddy.py::TestAllocation -v

# Run specific test
pytest tests/test_buddy.py::TestAllocation::test_simple_allocation -v
```

### Test Categories
- **Initialization Tests** - Memory setup and configuration
- **Allocation Tests** - Best-fit algorithm and buddy system
- **Deallocation Tests** - Memory freeing and block merging
- **Compaction Tests** - Memory reorganization
- **Edge Cases** - Boundary conditions and stress tests
- **Performance Tests** - Large-scale operation testing

### Expected Output
```
============================= test session starts ==============================
collected 30 items

tests/test_buddy.py::TestInitialization::test_initialization PASSED     [  3%]
tests/test_buddy.py::TestInitialization::test_custom_size PASSED        [  6%]
...
============================== 30 passed in 2.45s ==============================
```

---

## 11. Analytics

### Run Performance Analysis
```bash
cd analytics
python compare_policies.py
```

### Generated Visualizations
The script generates 5 PNG files:

1. **analytics_buddy_system.png** - Performance with buddy system
2. **analytics_no_buddy.png** - Performance without buddy system
3. **analytics_comparison.png** - Side-by-side comparison
4. **memory_state_buddy.png** - Memory state snapshot (buddy)
5. **memory_state_no_buddy.png** - Memory state snapshot (no buddy)

### Metrics Analyzed
- Memory usage trends over time
- Fragmentation patterns
- Block count evolution
- Allocation success rates
- Operation statistics

---


## 12. Future Scope

### Planned Enhancements
- [ ] **Multiple Allocation Strategies**
  - First-fit algorithm
  - Worst-fit algorithm
  - Next-fit algorithm

- [ ] **Priority-Based Allocation**
  - Process priorities
  - Real-time vs batch processes

- [ ] **Enhanced UI**
  - Drag-and-drop process placement
  - 3D memory visualization
  - Animation for compaction process

- [ ] **Advanced Features**
  - Memory paging simulation
  - Virtual memory support
  - Multi-level page tables

- [ ] **Real Data Integration**
  - Import actual OS memory traces
  - Process workload templates
  - Benchmark datasets

- [ ] **Performance Optimization**
  - Parallel allocation for multi-core
  - Caching strategies
  - Predictive allocation

---

## 13. References

### Academic Resources
1. **Operating System Concepts** (10th Edition)  
   Authors: Abraham Silberschatz, Peter B. Galvin, Greg Gagne  
   Topics: Memory management, allocation algorithms, paging

2. **Modern Operating Systems** (4th Edition)  
   Author: Andrew S. Tanenbaum  
   Topics: Memory management, buddy system, compaction

3. **The Art of Computer Programming, Volume 1**  
   Author: Donald E. Knuth  
   Topics: Memory allocation algorithms, complexity analysis

### Technical Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Official Docs](https://docs.python.org/3/)
- [pytest Documentation](https://docs.pytest.org/)
- [matplotlib Documentation](https://matplotlib.org/stable/contents.html)

### Research Papers
- "The Buddy System Memory Allocation" - Donald Knuth
- "Memory Management in Operating Systems" - ACM Journal
- "Fragmentation Analysis in Dynamic Memory Allocation"

---

## 14. Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 15. License

This project is licensed under the MIT License - see the  file for details.

---


<div align="center">

⭐ Star this repo if you find it helpful!

</div>

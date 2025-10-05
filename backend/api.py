"""
FastAPI Backend for Improvised Memory Manager
Provides REST API endpoints for memory management operations
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

from buddy_allocator import ImprovisedMemoryManager


# ============================================
# Pydantic Models for Request/Response
# ============================================

class InitializeRequest(BaseModel):
    total_memory: int = Field(..., gt=0, description="Total memory size in KB")


class AllocateRequest(BaseModel):
    process_name: str = Field(..., min_length=1, description="Process name")
    size: int = Field(..., gt=0, description="Memory size to allocate in KB")
    use_buddy: bool = Field(default=True, description="Use buddy system rounding")


class DeallocateRequest(BaseModel):
    process_name: str = Field(..., min_length=1, description="Process name to deallocate")


class MemoryResponse(BaseModel):
    success: bool
    message: str
    blocks: list
    used_memory: int
    free_memory: int
    total_memory: int
    fragmentation: float
    start_address: Optional[int] = None
    moved_processes: Optional[int] = None


# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title="Improvised Memory Manager API",
    description="REST API for memory allocation, deallocation, and compaction",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global memory manager instance
memory_manager: Optional[ImprovisedMemoryManager] = None


# ============================================
# API Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Improvised Memory Manager API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "initialize": "POST /initialize",
            "allocate": "POST /allocate",
            "deallocate": "POST /deallocate",
            "compact": "POST /compact",
            "status": "GET /status",
            "reset": "POST /reset"
        }
    }


@app.post("/initialize")
async def initialize_memory(request: InitializeRequest):
    """
    Initialize memory manager with specified size
    
    Args:
        request: InitializeRequest with total_memory
        
    Returns:
        Memory status after initialization
    """
    global memory_manager
    
    try:
        memory_manager = ImprovisedMemoryManager(request.total_memory)
        status = memory_manager.get_status()
        
        return {
            "success": True,
            "message": f"Memory initialized with {request.total_memory} KB",
            "blocks": status["blocks"],
            "total_memory": status["total_memory"],
            "used_memory": status["used_memory"],
            "free_memory": status["free_memory"],
            "fragmentation": status["fragmentation"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/allocate")
async def allocate_process(request: AllocateRequest):
    """
    Allocate memory to a process
    
    Args:
        request: AllocateRequest with process_name, size, and use_buddy
        
    Returns:
        Allocation result and updated memory status
    """
    if memory_manager is None:
        raise HTTPException(status_code=400, detail="Memory not initialized. Call /initialize first.")
    
    try:
        success, message, start_address = memory_manager.allocate(
            request.process_name,
            request.size,
            request.use_buddy
        )
        
        status = memory_manager.get_status()
        
        return {
            "success": success,
            "message": message,
            "start_address": start_address,
            "blocks": status["blocks"],
            "used_memory": status["used_memory"],
            "free_memory": status["free_memory"],
            "total_memory": status["total_memory"],
            "fragmentation": status["fragmentation"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deallocate")
async def deallocate_process(request: DeallocateRequest):
    """
    Deallocate memory for a process
    
    Args:
        request: DeallocateRequest with process_name
        
    Returns:
        Deallocation result and updated memory status
    """
    if memory_manager is None:
        raise HTTPException(status_code=400, detail="Memory not initialized")
    
    try:
        success, message = memory_manager.deallocate(request.process_name)
        status = memory_manager.get_status()
        
        return {
            "success": success,
            "message": message,
            "blocks": status["blocks"],
            "used_memory": status["used_memory"],
            "free_memory": status["free_memory"],
            "total_memory": status["total_memory"],
            "fragmentation": status["fragmentation"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compact")
async def compact_memory():
    """
    Compact memory by moving all allocated blocks together
    
    Returns:
        Compaction result and updated memory status
    """
    if memory_manager is None:
        raise HTTPException(status_code=400, detail="Memory not initialized")
    
    try:
        success, message, moved = memory_manager.compact()
        status = memory_manager.get_status()
        
        return {
            "success": success,
            "message": message,
            "moved_processes": moved,
            "blocks": status["blocks"],
            "used_memory": status["used_memory"],
            "free_memory": status["free_memory"],
            "total_memory": status["total_memory"],
            "fragmentation": status["fragmentation"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """
    Get current memory manager status
    
    Returns:
        Current memory statistics
    """
    if memory_manager is None:
        return {
            "initialized": False,
            "message": "Memory not initialized",
            "total_memory": 0,
            "used_memory": 0,
            "free_memory": 0,
            "blocks": [],
            "active_processes": 0,
            "fragmentation": 0
        }
    
    try:
        status = memory_manager.get_status()
        status["initialized"] = True
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_memory(total_memory: Optional[int] = None):
    """
    Reset memory manager
    
    Args:
        total_memory: Optional new total memory size
        
    Returns:
        Reset confirmation
    """
    if memory_manager is None:
        raise HTTPException(status_code=400, detail="Memory not initialized")
    
    try:
        memory_manager.reset(total_memory)
        status = memory_manager.get_status()
        
        return {
            "success": True,
            "message": "Memory reset successfully",
            "blocks": status["blocks"],
            "total_memory": status["total_memory"],
            "used_memory": status["used_memory"],
            "free_memory": status["free_memory"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "memory_initialized": memory_manager is not None
    }


# ============================================
# Startup Event
# ============================================

@app.on_event("startup")
async def startup_event():
    """Print startup information"""
    print("\n" + "=" * 50)
    print("🚀 Improvised Memory Manager API Server Started")
    print("=" * 50)
    print("📡 Server running at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔧 Alternative docs: http://localhost:8000/redoc")
    print("=" * 50 + "\n")


# ============================================
# Run Server
# ============================================

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
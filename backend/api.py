"""
FastAPI Backend for Improvised Memory Manager
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
import os

from buddy_allocator import ImprovisedMemoryManager


# ---------- Request / Response Models ----------

class InitializeRequest(BaseModel):
    total_memory: int = Field(..., gt=0, description="Total memory in KB")


class AllocateRequest(BaseModel):
    process_name: str = Field(..., min_length=1)
    size: int = Field(..., gt=0)
    use_buddy: bool = Field(default=True)


class DeallocateRequest(BaseModel):
    process_name: str = Field(..., min_length=1)


# ---------- App ----------

app = FastAPI(
    title="Improvised Memory Manager API",
    description="REST API for memory allocation, deallocation, and compaction",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend if it exists next to this file
_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(_frontend_dir):
    app.mount("/static", StaticFiles(directory=_frontend_dir), name="static")

memory_manager: Optional[ImprovisedMemoryManager] = None


# ---------- Endpoints ----------

@app.get("/")
async def root():
    index = os.path.join(_frontend_dir, "index.html")
    if os.path.isfile(index):
        return FileResponse(index)
    return {"name": "Improvised Memory Manager API", "version": "2.0.0", "docs": "/docs"}


@app.post("/initialize")
async def initialize_memory(req: InitializeRequest):
    global memory_manager
    try:
        memory_manager = ImprovisedMemoryManager(req.total_memory)
        return {"success": True, "message": f"Memory initialized with {req.total_memory} KB", **memory_manager.get_status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/allocate")
async def allocate_process(req: AllocateRequest):
    if memory_manager is None:
        raise HTTPException(status_code=400, detail="Memory not initialized. Call /initialize first.")
    try:
        success, message, start_address = memory_manager.allocate(req.process_name, req.size, req.use_buddy)
        return {"success": success, "message": message, "start_address": start_address, **memory_manager.get_status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deallocate")
async def deallocate_process(req: DeallocateRequest):
    if memory_manager is None:
        raise HTTPException(status_code=400, detail="Memory not initialized")
    try:
        success, message = memory_manager.deallocate(req.process_name)
        return {"success": success, "message": message, **memory_manager.get_status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compact")
async def compact_memory():
    if memory_manager is None:
        raise HTTPException(status_code=400, detail="Memory not initialized")
    try:
        success, message, moved = memory_manager.compact()
        return {"success": success, "message": message, "moved_processes": moved, **memory_manager.get_status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    if memory_manager is None:
        return {"initialized": False, "total_memory": 0, "used_memory": 0, "free_memory": 0,
                "blocks": [], "active_processes": 0, "fragmentation": 0, "process_list": []}
    try:
        status = memory_manager.get_status()
        status["initialized"] = True
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
async def reset_memory(total_memory: Optional[int] = None):
    if memory_manager is None:
        raise HTTPException(status_code=400, detail="Memory not initialized")
    try:
        memory_manager.reset(total_memory)
        return {"success": True, "message": "Memory reset successfully", **memory_manager.get_status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy", "memory_initialized": memory_manager is not None}


@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 52)
    print("  Improvised Memory Manager API  v2.0")
    print("=" * 52)
    print("  http://localhost:8000        → Frontend UI")
    print("  http://localhost:8000/docs   → Swagger docs")
    print("=" * 52 + "\n")


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True, log_level="info")

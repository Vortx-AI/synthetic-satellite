"""Memory system endpoints for the Vortx API"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from ..core.memory import MemorySystem
from ..utils.satellite_utils import setup_logging

router = APIRouter()

class MemoryEntry(BaseModel):
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    tags: List[str] = []

class MemoryResponse(BaseModel):
    memory_id: str
    metadata: Dict[str, Any]
    created_at: datetime

@router.post("/store", response_model=MemoryResponse)
async def store_memory(entry: MemoryEntry):
    """Store data in the memory system"""
    try:
        memory = MemorySystem()
        memory_id = memory.store(
            data=entry.data,
            metadata=entry.metadata,
            tags=entry.tags
        )
        
        return MemoryResponse(
            memory_id=memory_id,
            metadata=entry.metadata,
            created_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/retrieve/{memory_id}")
async def retrieve_memory(memory_id: str):
    """Retrieve data from memory"""
    try:
        memory = MemorySystem()
        result = memory.retrieve(memory_id)
        if not result:
            raise HTTPException(status_code=404, detail="Memory not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_memory(
    query: str = Query(..., description="Search query"),
    tags: List[str] = Query(None, description="Filter by tags"),
    limit: int = Query(10, description="Maximum number of results")
):
    """Search the memory system"""
    try:
        memory = MemorySystem()
        results = memory.search(
            query=query,
            tags=tags,
            limit=limit
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a memory entry"""
    try:
        memory = MemorySystem()
        success = memory.delete(memory_id)
        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")
        return {"status": "success", "message": f"Deleted memory {memory_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_memory_stats():
    """Get memory system statistics"""
    try:
        memory = MemorySystem()
        stats = memory.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
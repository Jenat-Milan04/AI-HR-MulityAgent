from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from .models import (
    HRRequest, HRResponse, MemoryEntry, MemoryResponse, 
    AuditLog, HealthResponse
)
from ..services import orchestrator, audit_logger
from ..memory import stm, ltm

router = APIRouter()

@router.post("/request", response_model=HRResponse)
async def submit_hr_request(request: HRRequest):
    """Submit an HR request and get a response."""
    try:
        result = await orchestrator.process_request(request.user_id, request.message)
        return HRResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/audit", response_model=List[AuditLog])
async def get_audit_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to retrieve"),
    offset: int = Query(0, ge=0, description="Number of logs to skip")
):
    """Retrieve audit logs with optional filtering."""
    try:
        logs = await audit_logger.get_logs(user_id, limit, offset)
        return [AuditLog(**log) for log in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/memory/{user_id}", response_model=MemoryResponse)
async def get_user_memory(user_id: str):
    """Retrieve user's STM and LTM entries."""
    try:
        stm_entries = await stm.get_entries(user_id)
        ltm_entries = await ltm.get_entries(user_id)
        
        return MemoryResponse(
            user_id=user_id,
            stm_entries=stm_entries,
            ltm_entries=ltm_entries
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/memory")
async def add_memory_entry(entry: MemoryEntry):
    """Manually add a memory entry."""
    try:
        # Add to STM
        await stm.add_entry(entry.user_id, entry.message)
        
        # Try to add to LTM based on significance
        added_to_ltm = await ltm.add_entry_if_significant(entry.user_id, entry.message)
        
        return {
            "message": "Memory entry added",
            "added_to_stm": True,
            "added_to_ltm": added_to_ltm
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()
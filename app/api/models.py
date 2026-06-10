from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class HRRequest(BaseModel):
    """Request model for HR queries."""
    user_id: str = Field(..., description="Unique identifier for the user")
    message: str = Field(..., min_length=1, description="The user's HR request or question")

class HRResponse(BaseModel):
    """Response model for HR queries."""
    user_id: str
    response: str
    intent: str
    confidence: float
    agent: str
    status: str

class MemoryEntry(BaseModel):
    """Memory entry model."""
    user_id: str
    message: str
    significance: Optional[float] = None
    timestamp: Optional[datetime] = None

class MemoryResponse(BaseModel):
    """Response model for memory retrieval."""
    user_id: str
    stm_entries: List[Dict[str, Any]]
    ltm_entries: List[Dict[str, Any]]

class AuditLog(BaseModel):
    """Audit log entry model."""
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    user_id: str
    request: str
    intent: Optional[str] = None
    agent: Optional[str] = None
    response: str
    status: str

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
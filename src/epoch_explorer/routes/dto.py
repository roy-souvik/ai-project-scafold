from pydantic import BaseModel
from typing import Optional, Dict, Any


class ChatMessage(BaseModel):
    """Chat message"""
    content: str
    session_id: Optional[str] = None
    response_mode: str = "concise"  # concise|verbose|internal


class ChatResponse(BaseModel):
    """Chat response"""
    success: bool
    content: str
    session_id: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class QueryRequest(BaseModel):
    """Query request"""
    question: str
    response_mode: str = "concise"
    doc_id: Optional[str] = None


class IngestRequest(BaseModel):
    """Document ingestion request"""
    text: Optional[str] = None
    doc_id: Optional[str] = None
    source_type: Optional[str] = "txt"


class HealRequest(BaseModel):
    """Healing request"""
    doc_id: str
    current_quality: float

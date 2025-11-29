"""
FastAPI Endpoints for RAG Agent

Supports:
- Chat interface (admin + user modes)
- Query/Retrieval
- Document ingestion
- Healing/Optimization
"""

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import asyncio
from datetime import datetime
import tempfile
import os

app = FastAPI(
    title="RAG Agent API",
    description="Chat-enhanced Retrieval-Augmented Generation",
    version="1.0.0"
)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

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


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Health check"""
    return {
        "status": "online",
        "service": "RAG Agent API",
        "version": "1.0.0",
        "endpoints": [
            "/docs",
            "/chat",
            "/chat/query",
            "/chat/ingest",
            "/chat/heal"
        ]
    }


# Chat Endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Chat endpoint - processes chat messages
    
    Supports commands:
    - "query: ..." - Ask question
    - "ingest_file: ..." - Ingest document
    - "heal: doc_id|quality" - Heal document
    - "set_mode: concise|verbose|internal" - Change response mode
    """
    try:
        from src.rag.chat_interface import ChatRAGInterface, ChatCommand, ChatSession
        from src.rag.agents.langgraph_agent.langgraph_rag_agent import LangGraphRAGAgent
        
        # Initialize if needed
        if not hasattr(app, 'chat_interface'):
            agent = LangGraphRAGAgent()
            app.chat_interface = ChatRAGInterface(agent.ask_question)
        
        # Get or create session
        session_id = message.session_id
        if not session_id:
            session = app.chat_interface.create_session()
            session_id = session.session_id
        else:
            session = app.chat_interface.get_session(session_id)
            if not session:
                session = app.chat_interface.create_session()
                session_id = session.session_id
        
        # Process message
        response = await app.chat_interface.process_message(
            text=message.content,
            session_id=session_id,
            response_mode=message.response_mode
        )
        
        return ChatResponse(
            success=response.status == "success",
            content=response.content,
            session_id=session_id,
            metadata={
                "command_type": response.command_type.value if response.command_type else None,
                "processing_time_ms": response.processing_time_ms
            },
            error=response.error
        )
    
    except Exception as e:
        return ChatResponse(
            success=False,
            content="",
            session_id=message.session_id or "unknown",
            error=str(e)
        )


@app.post("/chat/query")
async def chat_query(request: QueryRequest):
    """Query endpoint with response mode support"""
    try:
        from src.rag.agents.langgraph_agent.langgraph_rag_agent import LangGraphRAGAgent
        
        agent = LangGraphRAGAgent()
        result = agent.ask_question(
            question=request.question,
            response_mode=request.response_mode,
            doc_id=request.doc_id
        )
        
        return {
            "success": result.get("success", False),
            "answer": result.get("answer", ""),
            "metadata": {
                "quality": result.get("retrieval_quality", 0),
                "sources": len(result.get("source_docs", [])),
                "response_mode": request.response_mode
            }
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/chat/ingest")
async def chat_ingest(request: IngestRequest):
    """Ingest document via API"""
    try:
        from src.rag.agents.langgraph_agent.langgraph_rag_agent import LangGraphRAGAgent
        
        agent = LangGraphRAGAgent()
        result = agent.ingest_document(
            text=request.text or "",
            doc_id=request.doc_id or f"doc_{datetime.now().timestamp()}"
        )
        
        return {
            "success": result.get("success", False),
            "doc_id": result.get("doc_id"),
            "chunks_saved": result.get("chunks_saved", 0),
            "errors": result.get("errors", [])
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/chat/ingest-file")
async def chat_ingest_file(file: UploadFile = File(...)):
    """Ingest file via multipart upload"""
    try:
        from src.rag.agents.langgraph_agent.langgraph_rag_agent import LangGraphRAGAgent
        
        agent = LangGraphRAGAgent()
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Ingest from path
            result = agent.invoke(
                operation="ingest_from_path",
                path=tmp_path,
                recursive=False,
                file_type="auto"
            )
            
            return {
                "success": result.get("success", False),
                "documents_ingested": result.get("documents_ingested", 0),
                "errors": result.get("errors", [])
            }
        finally:
            os.remove(tmp_path)
    
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/chat/ingest-table")
async def chat_ingest_table(table_name: str):
    """Ingest database table"""
    try:
        from src.rag.agents.langgraph_agent.langgraph_rag_agent import LangGraphRAGAgent
        
        agent = LangGraphRAGAgent()
        result = agent.invoke(
            operation="ingest_sqlite_table",
            table_name=table_name
        )
        
        return {
            "success": result.get("success", False),
            "records_processed": result.get("records_processed", 0),
            "chunks_saved": result.get("total_chunks_saved", 0),
            "error": result.get("error")
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/chat/heal")
async def chat_heal(request: HealRequest):
    """Heal document with RL agent"""
    try:
        from src.rag.agents.langgraph_agent.langgraph_rag_agent import LangGraphRAGAgent
        
        agent = LangGraphRAGAgent()
        
        # Ask question which triggers healing
        result = agent.ask_question(
            question=f"Evaluate {request.doc_id}",
            doc_id=request.doc_id,
            response_mode="verbose"
        )
        
        return {
            "success": result.get("success", False),
            "doc_id": request.doc_id,
            "action": result.get("rl_action", "SKIP"),
            "optimization_applied": result.get("optimization_applied", False),
            "metadata": {
                "original_quality": request.current_quality,
                "expected_improvement": result.get("rl_recommendation", {}).get("expected_improvement", 0)
            }
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/chat/status")
async def chat_status():
    """Get chat system status"""
    try:
        from src.rag.agents.langgraph_agent.langgraph_rag_agent import LangGraphRAGAgent
        
        agent = LangGraphRAGAgent()
        
        return {
            "status": "online",
            "services": {
                "llm": "initialized" if agent.llm_service else "failed",
                "vectordb": "initialized" if agent.vectordb_service else "failed",
                "rl_agent": "initialized" if agent.rl_healing_agent else "not_available"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Legacy endpoints (for backwards compatibility)
@app.post("/add")
async def add_doc(request: Request):
    """Legacy document addition endpoint"""
    try:
        data = await request.json()
        text = data.get("text")
        if not text:
            return {"error": "Missing 'text' field"}
        
        from src.rag.agents.langgraph_agent.langgraph_rag_agent import LangGraphRAGAgent
        agent = LangGraphRAGAgent()
        result = agent.ingest_document(text, doc_id=data.get("doc_id", "doc_default"))
        
        return result
    except Exception as e:
        return {"error": str(e)}


@app.post("/query")
async def query_doc(request: Request):
    """Legacy query endpoint"""
    try:
        data = await request.json()
        question = data.get("question")
        if not question:
            return {"error": "Missing 'question' field"}
        
        from src.rag.agents.langgraph_agent.langgraph_rag_agent import LangGraphRAGAgent
        agent = LangGraphRAGAgent()
        result = agent.ask_question(question)
        
        return result
    except Exception as e:
        return {"error": str(e)}

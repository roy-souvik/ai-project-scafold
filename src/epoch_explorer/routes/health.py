from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])

@router.get("/")
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


@router.post("/add")
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


@router.post("/query")
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

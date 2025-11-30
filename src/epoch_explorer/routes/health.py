from fastapi import APIRouter, Request
from epoch_explorer.services.rag_pipeline import query_llm, query_rag
import traceback

router = APIRouter(tags=["health"])

@router.get("/")
def root():
    """Health check"""
    return {
        "status": "online",
        "service": "API based AI app with AI",
        "version": "1.0.0",
    }


# @router.post("/add")
# async def add_doc(request: Request):
#     """Document addition endpoint"""
#     try:
#         data = await request.json()
#         text = data.get("text")
#         if not text:
#             return {"error": "Missing 'text' field"}

#         from src.rag.agents.langgraph_agent.langgraph_rag_agent import LangGraphRAGAgent
#         agent = LangGraphRAGAgent()
#         result = agent.ingest_document(text, doc_id=data.get("doc_id", "doc_default"))

#         return result
#     except Exception as e:
#         return {"error": str(e)}


@router.post("/query")
async def query_doc(request: Request):
    try:
        data = await request.json()
        question = data.get("question")
        if not question:
            return {"error": "Missing 'question' field"}
        return {"answer": query_llm(question)}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}
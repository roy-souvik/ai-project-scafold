from .chat import router as chat_router
from .health import router as health_router
from .mcp_api import router as mcp_router

__all__ = ["chat_router", "health_router", "mcp_router"]

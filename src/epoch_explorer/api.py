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

# ...existing code...

@app.get("/")
def root():
    """Health check"""
    return {
        "status": "online",
        "service": "RAG Agent API",
        "version": "1.0.0",
        "endpoints": [
            "/docs",
            "/health"
        ]
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}
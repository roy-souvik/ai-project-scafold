from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3
from datetime import datetime
import json
from typing import List, Optional

try:
	import ollama
	OLLAMA_AVAILABLE = True
except ImportError:
	OLLAMA_AVAILABLE = False

from epoch_explorer.mcp.mcp_tools import TOOLS, TOOL_SCHEMAS

router = APIRouter(prefix="/mcp", tags=["mcp"])

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_llm_db():
	"""Initialize LLM interactions logging database"""
	conn = sqlite3.connect('llm_interactions.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS llm_requests
	             (id INTEGER PRIMARY KEY, timestamp TEXT, prompt TEXT,
	              tools_available TEXT, response TEXT)''')
	c.execute('''CREATE TABLE IF NOT EXISTS llm_tool_usage
	             (id INTEGER PRIMARY KEY, timestamp TEXT, request_id INTEGER,
	              tool_name TEXT, tool_args TEXT, tool_result TEXT)''')
	conn.commit()
	conn.close()

init_llm_db()

# ============================================================================
# MODELS
# ============================================================================

class QueryRequest(BaseModel):
	query: str
	model: str = "llama3.2"
	use_tools: bool = True

class ToolUsage(BaseModel):
	tool_name: str
	arguments: dict
	result: str

class QueryResponse(BaseModel):
	response: str
	tools_used: List[ToolUsage]
	request_id: int

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
	"""Process user query with Ollama and MCP tools"""

	if not OLLAMA_AVAILABLE:
		raise HTTPException(status_code=503, detail="Ollama not available")

	# Log request
	conn = sqlite3.connect('llm_interactions.db')
	c = conn.cursor()

	tools_used = []
	tool_names = [t["function"]["name"] for t in TOOL_SCHEMAS]

	c.execute("INSERT INTO llm_requests VALUES (NULL, ?, ?, ?, ?)",
	          (datetime.now().isoformat(), request.query,
	           json.dumps(tool_names), ""))
	request_id = c.lastrowid
	conn.commit()

	try:
		# Call Ollama with tools
		response = ollama.chat(
			model=request.model,
			messages=[{'role': 'user', 'content': request.query}],
			tools=TOOL_SCHEMAS if request.use_tools else None
		)

		final_response = response['message']['content']

		# Handle tool calls
		if request.use_tools and response['message'].get('tool_calls'):
			for tool_call in response['message']['tool_calls']:
				tool_name = tool_call['function']['name']
				tool_args = tool_call['function']['arguments']

				# Execute tool from FastMCP registry
				if tool_name in TOOLS:
					tool_result = TOOLS[tool_name](**tool_args)
				else:
					tool_result = f"Error: Unknown tool {tool_name}"

				# Log tool usage
				c.execute("INSERT INTO llm_tool_usage VALUES (NULL, ?, ?, ?, ?, ?)",
				          (datetime.now().isoformat(), request_id, tool_name,
				           json.dumps(tool_args), tool_result))
				conn.commit()

				tools_used.append(ToolUsage(
					tool_name=tool_name,
					arguments=tool_args,
					result=tool_result
				))

				# Send result back to Ollama
				messages = [
					{'role': 'user', 'content': request.query},
					response['message'],
					{'role': 'tool', 'content': tool_result}
				]

				response = ollama.chat(model=request.model, messages=messages)
				final_response = response['message']['content']

		# Update final response
		c.execute("UPDATE llm_requests SET response = ? WHERE id = ?",
		          (final_response, request_id))
		conn.commit()

		return QueryResponse(
			response=final_response,
			tools_used=tools_used,
			request_id=request_id
		)

	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
	finally:
		conn.close()

@router.get("/tools")
async def list_tools():
	"""List available MCP tools"""
	return {"tools": TOOL_SCHEMAS}

@router.get("/logs/requests")
async def get_request_logs(limit: int = 10):
	"""Get recent LLM request logs"""
	conn = sqlite3.connect('llm_interactions.db')
	c = conn.cursor()
	c.execute("SELECT * FROM llm_requests ORDER BY id DESC LIMIT ?", (limit,))
	rows = c.fetchall()
	conn.close()

	return {"logs": [
		{
			"id": r[0], "timestamp": r[1], "prompt": r[2],
			"tools_available": json.loads(r[3]), "response": r[4]
		} for r in rows
	]}

@router.get("/logs/tools")
async def get_tool_logs(limit: int = 10):
	"""Get recent tool usage logs"""
	conn = sqlite3.connect('llm_interactions.db')
	c = conn.cursor()
	c.execute("SELECT * FROM llm_tool_usage ORDER BY id DESC LIMIT ?", (limit,))
	rows = c.fetchall()
	conn.close()

	return {"logs": [
		{
			"id": r[0], "timestamp": r[1], "request_id": r[2],
			"tool_name": r[3], "tool_args": json.loads(r[4]), "tool_result": r[5]
		} for r in rows
	]}

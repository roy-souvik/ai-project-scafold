import json
import sqlite3
from datetime import datetime
from fastmcp import FastMCP
from pathlib import Path
import sys

# Add src to path for imports
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from epoch_explorer.database.db.connection import get_connection

# Initialize logging database
def init_mcp_db():
	"""Initialize MCP logging database"""
	conn = sqlite3.connect('mcp_logs.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS tool_calls
	             (id INTEGER PRIMARY KEY, timestamp TEXT, tool_name TEXT,
	              arguments TEXT, result TEXT)''')
	c.execute('''CREATE TABLE IF NOT EXISTS resource_reads
	             (id INTEGER PRIMARY KEY, timestamp TEXT, uri TEXT, content TEXT)''')
	conn.commit()
	conn.close()

init_mcp_db()

# Create FastMCP instance
mcp = FastMCP("Demo MCP Server")

# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

@mcp.tool()
def calculate(operation: str, a: float, b: float) -> str:
	"""Perform basic math calculations.

	Args:
		operation: One of 'add', 'subtract', 'multiply', 'divide'
		a: First number
		b: Second number
	"""
	conn = sqlite3.connect('mcp_logs.db')
	c = conn.cursor()

	if operation == "add":
		result = str(a + b)
	elif operation == "subtract":
		result = str(a - b)
	elif operation == "multiply":
		result = str(a * b)
	elif operation == "divide":
		result = str(a / b) if b != 0 else "Error: Division by zero"
	else:
		result = "Invalid operation"

	c.execute("INSERT INTO tool_calls VALUES (NULL, ?, ?, ?, ?)",
	          (datetime.now().isoformat(), "calculate",
	           json.dumps({"operation": operation, "a": a, "b": b}), result))
	conn.commit()
	conn.close()

	return result

@mcp.tool()
def get_time() -> str:
	"""Get current timestamp"""
	conn = sqlite3.connect('mcp_logs.db')
	c = conn.cursor()

	result = datetime.now().isoformat()

	c.execute("INSERT INTO tool_calls VALUES (NULL, ?, ?, ?, ?)",
	          (datetime.now().isoformat(), "get_time", "{}", result))
	conn.commit()
	conn.close()

	return result

@mcp.tool()
def get_database_info() -> str:
	"""Get information from the project database

	Returns database connection status and basic info
	"""
	conn = sqlite3.connect('mcp_logs.db')
	c = conn.cursor()

	try:
		db_conn = get_connection()
		result = "Database connection successful"
		c.execute("INSERT INTO tool_calls VALUES (NULL, ?, ?, ?, ?)",
		          (datetime.now().isoformat(), "get_database_info", "{}", result))
	except Exception as e:
		result = f"Database connection failed: {str(e)}"
		c.execute("INSERT INTO tool_calls VALUES (NULL, ?, ?, ?, ?)",
		          (datetime.now().isoformat(), "get_database_info", "{}", result))

	conn.commit()
	conn.close()

	return result

@mcp.tool()
def search_database(query: str) -> str:
	"""Search in database

	Args:
		query: Search query
	"""
	conn = sqlite3.connect('mcp_logs.db')
	c = conn.cursor()

	# Mock search result
	result = f"Found 3 results for '{query}'"

	c.execute("INSERT INTO tool_calls VALUES (NULL, ?, ?, ?, ?)",
	          (datetime.now().isoformat(), "search_database",
	           json.dumps({"query": query}), result))
	conn.commit()
	conn.close()

	return result

@mcp.resource("config://settings")
def get_settings() -> str:
	"""App settings configuration"""
	conn = sqlite3.connect('mcp_logs.db')
	c = conn.cursor()

	content = json.dumps({"theme": "dark", "version": "1.0", "api_version": "1.0.0"})

	c.execute("INSERT INTO resource_reads VALUES (NULL, ?, ?, ?)",
	          (datetime.now().isoformat(), "config://settings", content))
	conn.commit()
	conn.close()

	return content

# ============================================================================
# TOOL REGISTRY
# ============================================================================

def get_tools_registry():
	"""Get tool functions registry from FastMCP"""
	tools = {}
	for tool_name, tool_info in mcp._tool_manager._tools.items():
		tools[tool_name] = tool_info.fn
	return tools

def get_tool_schemas():
	"""Convert FastMCP tools to Ollama format"""
	schemas = []
	for tool_name, tool_info in mcp._tool_manager._tools.items():
		schemas.append({
			"type": "function",
			"function": {
				"name": tool_name,
				"description": tool_info.description or "",
				"parameters": tool_info.parameters
			}
		})
	return schemas

# Export for use in API
TOOLS = get_tools_registry()
TOOL_SCHEMAS = get_tool_schemas()

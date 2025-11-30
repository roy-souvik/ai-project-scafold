import streamlit as st
import requests
import json

st.set_page_config(page_title="MCP Demo", page_icon="🔧")

st.title("🔧 MCP Tools Demo")

st.markdown("""
This demo showcases the Model Context Protocol (MCP) integration with FastAPI and Ollama.
MCP tools allow language models to interact with external systems and perform actions.
""")

# Sidebar configuration
st.sidebar.header("Configuration")
api_url = st.sidebar.text_input("API URL", value="http://localhost:8000")
model = st.sidebar.selectbox("Model", ["llama3.2", "llama2", "mistral"])
use_tools = st.sidebar.checkbox("Use Tools", value=True)

# Initialize chat history
if "messages" not in st.session_state:
	st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
	with st.chat_message(message["role"]):
		st.markdown(message["content"])
		if "tools_used" in message and message["tools_used"]:
			with st.expander("🔧 Tools Used"):
				for tool in message["tools_used"]:
					col1, col2 = st.columns([1, 2])
					with col1:
						st.write(f"**{tool['tool_name']}**")
					with col2:
						st.json(tool['arguments'])
					st.caption(f"Result: {tool['result']}")

# Chat input
if prompt := st.chat_input("Ask me anything..."):
	# Display user message
	st.session_state.messages.append({"role": "user", "content": prompt})
	with st.chat_message("user"):
		st.markdown(prompt)

	# Call API
	with st.chat_message("assistant"):
		with st.spinner("Thinking..."):
			try:
				response = requests.post(
					f"{api_url}/mcp/query",
					json={"query": prompt, "model": model, "use_tools": use_tools},
					timeout=30
				)
				result = response.json()

				st.markdown(result["response"])

				if result["tools_used"]:
					with st.expander("🔧 Tools Used"):
						for tool in result["tools_used"]:
							st.write(f"**Tool: {tool['tool_name']}**")
							st.json({
								"arguments": tool['arguments'],
								"result": tool['result']
							})

				st.session_state.messages.append({
					"role": "assistant",
					"content": result["response"],
					"tools_used": result["tools_used"]
				})
			except requests.exceptions.ConnectionError:
				st.error(f"❌ Cannot connect to API at {api_url}")
				st.info("Make sure the FastAPI server is running on the configured URL")
			except Exception as e:
				st.error(f"❌ Error: {str(e)}")

# Sidebar: Available Tools
st.sidebar.header("Available Tools")
try:
	tools_response = requests.get(f"{api_url}/mcp/tools", timeout=5)
	if tools_response.status_code == 200:
		tools = tools_response.json()["tools"]
		for tool in tools:
			with st.sidebar.expander(f"📌 {tool['function']['name']}"):
				st.write(tool['function']['description'])
				if tool['function']['parameters'].get('properties'):
					st.write("**Parameters:**")
					st.json(tool['function']['parameters']['properties'])
	else:
		st.sidebar.warning("Could not fetch tools list")
except:
	st.sidebar.warning("API not available")

# Sidebar: Recent Logs
st.sidebar.header("Recent Logs")
if st.sidebar.button("Refresh Logs"):
	try:
		logs_response = requests.get(f"{api_url}/mcp/logs/requests?limit=3", timeout=5)
		if logs_response.status_code == 200:
			logs = logs_response.json()["logs"]
			for log in logs:
				with st.sidebar.expander(f"📝 Request #{log['id']}"):
					st.write(f"**Time:** {log['timestamp']}")
					st.write(f"**Prompt:** {log['prompt']}")
					st.write(f"**Response:** {log['response']}")
	except:
		st.sidebar.error("Could not fetch logs")

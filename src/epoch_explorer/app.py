import streamlit as st
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Page config
st.set_page_config(
    page_title="RAG Assistant Hub",
    page_icon="🤖",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio(
    "Select Page",
    [
        "🏠 Home",
        "💬 User Chat",
        "⚙️ Admin Chat",
        "🔍 Query",
        "📊 Dashboard"
    ]
)

st.sidebar.divider()
st.sidebar.info("💡 Select a page to get started")

# Routes
if page == "🏠 Home":
    st.title("🤖 RAG Assistant Hub")
    st.markdown("""
    Welcome to the RAG (Retrieval-Augmented Generation) Assistant Hub!
    
    Choose your role:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💬 User Mode")
        st.write("""
        - Ask questions about documents
        - Get concise or detailed answers
        - View source documents
        - Export chat history
        """)
        if st.button("Go to User Chat →", use_container_width=True):
            st.switch_page("pages/chat_user.py")
    
    with col2:
        st.subheader("⚙️ Admin Mode")
        st.write("""
        - Ingest new documents
        - Heal and optimize embeddings
        - Monitor system health
        - Advanced analytics
        """)
        if st.button("Go to Admin Chat →", use_container_width=True):
            st.switch_page("pages/chat_rag_admin.py")

elif page == "💬 User Chat":
    from pages.chat_user import show
    show()

elif page == "⚙️ Admin Chat":
    from pages.chat_rag_admin import show_admin_chat
    show_admin_chat()

elif page == "🔍 Query":
    st.title("🔍 Direct Query")
    st.markdown("Ask a question directly without chat history")
    
    query = st.text_input("Your question")
    mode = st.selectbox("Response Mode", ["concise", "verbose"])
    
    if st.button("Search"):
        if query:
            with st.spinner("Searching..."):
                try:
                    from src.rag.agents.langgraph_agent.langgraph_rag_agent import LangGraphRAGAgent
                    agent = LangGraphRAGAgent()
                    result = agent.ask_question(query, response_mode=mode)
                    
                    if result.get("success"):
                        st.success("✓ Found answer!")
                        st.write(result.get("answer"))
                    else:
                        st.error("Query failed")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

elif page == "📊 Dashboard":
    st.title("📊 System Dashboard")
    st.markdown("View system health and metrics")
    
    try:
        from src.rag.agents.langgraph_agent.langgraph_rag_agent import LangGraphRAGAgent
        
        agent = LangGraphRAGAgent()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("LLM Service", "✓ Online" if agent.llm_service else "✗ Offline")
        
        with col2:
            st.metric("Vector DB", "✓ Online" if agent.vectordb_service else "✗ Offline")
        
        with col3:
            st.metric("RL Agent", "✓ Ready" if agent.rl_healing_agent else "⚠️ N/A")
    
    except Exception as e:
        st.error(f"Dashboard error: {str(e)}")

#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Add src directory to path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Configure Streamlit page
st.set_page_config(
    page_title="FinBot - Financial Literacy Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Header style inspired by Greenh2 */
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #2E7D32, #4CAF50);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }

    /* Compact, consistent buttons across the app */
    .stButton > button,
    .stDownloadButton > button,
    .stLinkButton > button {
        width: 100%;
        min-height: 40px;
        padding: 0.5rem 0.9rem !important;
        background: #1E88E5 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        white-space: normal !important; /* allow wrapping without large height */
        line-height: 1.2 !important;
        box-shadow: none !important;
        transition: background 0.15s ease !important;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stLinkButton > button:hover {
        background: #1565C0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
    }

    /* Center and soften captions under feature buttons */
    [data-testid="stCaptionContainer"] p, .stCaption, .stMarkdown small {
        text-align: center;
        color: #6b7280;
        margin-top: 0.35rem;
        margin-bottom: 0;
        font-size: 0.9rem;
    }

    /* Reduce column inner padding to tidy row */
    [data-testid="column"] > div { padding-right: 0.5rem; padding-left: 0.5rem; }
</style>
""", unsafe_allow_html=True)

def main_streamlit():
    """Main Streamlit application."""
    
    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    
    # Header (use Greenh2-like design)
    st.markdown(
        """
        <div class="main-header">
            <h1>💰 FinBot - Financial Literacy Assistant</h1>
            <p>Your comprehensive financial education companion</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Navigation based on current page
    if st.session_state.current_page == "home":
        show_home_page()
    elif st.session_state.current_page == "chatbot":
        show_chatbot_page()
    elif st.session_state.current_page == "learning_module":
        show_learning_module_page()
    elif st.session_state.current_page == "document_chat":
        show_document_chat_page()

def show_home_page():
    """Display the home page with clickable feature cards."""
    
    st.markdown("## Choose Your Financial Assistant Feature")
    
    # Create three columns for feature buttons (compact)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        clicked = st.button("Financial Chatbot", key="chatbot_card", use_container_width=True)
        st.caption("Ask questions about financial concepts and get expert guidance")
        if clicked:
            st.session_state.current_page = "chatbot"
            st.rerun()
    
    with col2:
        clicked = st.button("Learning Module Creator", key="learning_card", use_container_width=True)
        st.caption("Generate comprehensive educational handouts on financial topics")
        if clicked:
            st.session_state.current_page = "learning_module"
            st.rerun()
    
    with col3:
        clicked = st.button("Document Chat", key="document_card", use_container_width=True)
        st.caption("Upload and chat with your financial documents (Coming Soon)")
        if clicked:
            st.session_state.current_page = "document_chat"
            st.rerun()
    
    # System Status Section
    st.markdown("---")
    st.markdown("### System Status")
    
    try:
        from rag_pipeline import create_rag_pipeline
        pipeline = create_rag_pipeline()
        status = pipeline.get_system_status()
        
        if status.get("status") == "healthy":
            st.success("All systems operational")
        else:
            st.error("System initialization error")
            
    except Exception as e:
        st.warning(f"Could not check system status: {str(e)}")

def show_chatbot_page():
    """Display the chatbot interface with chat history."""
    
    # Back to home button
    if st.button("Back to Home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    st.markdown("## Financial Chatbot")
    st.markdown("Ask me anything about finance, investments, or personal money management!")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for i, (question, answer) in enumerate(st.session_state.chat_history):
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            st.markdown(answer)
    
    # Chat input
    if prompt := st.chat_input("Ask your financial question..."):
        # Add user message to chat
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base..."):
                try:
                    from rag_pipeline import create_rag_pipeline
                    pipeline = create_rag_pipeline()
                    
                    # Use stateless query (no chat history)
                    response = pipeline.query(prompt)
                    answer = response["answer"]
                    
                    st.markdown(answer)
                    
                    # Add to chat history
                    st.session_state.chat_history.append((prompt, answer))
                    
                    # Show sources if available
                    if response.get("sources"):
                        with st.expander("View Sources"):
                            for i, source in enumerate(response["sources"][:3], 1):
                                metadata = source.get('metadata', {})
                                
                                # Extract essential information
                                filename = metadata.get('filename', 'Unknown')
                                source_path = metadata.get('source', '')
                                page_number = metadata.get('page_number', 'N/A')
                                
                                # Display simplified source info
                                st.markdown(f"**Source {i}** (Score: {source['score']:.3f})")
                                st.markdown(f"📄 **File:** {filename}")
                                if source_path:
                                    st.markdown(f"📁 **Path:** {source_path}")
                                if page_number and page_number != 'N/A':
                                    st.markdown(f"📖 **Page:** {page_number}")
                                
                                # Show a preview of the content
                                st.markdown(f"**Preview:** {source['text'][:200]}...")
                                st.markdown("---")
                    
                except Exception as e:
                    answer = f"I apologize, but I encountered an error: {str(e)}"
                    st.error(answer)
                    # Still add error to history
                    st.session_state.chat_history.append((prompt, answer))
    
    # Clear chat history button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

def show_learning_module_page():
    """Display the learning module creation interface."""
    
    # Back to home button
    if st.button("Back to Home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    st.markdown("## Create Learning Module")
    st.markdown("Generate comprehensive educational handouts on financial topics using our AI agents.")
    
    # Topic input
    topic = st.text_input(
        "Enter the financial topic you want to learn about:",
        placeholder="e.g., Mutual Funds, Personal Finance Basics, Investment Strategies"
    )
    
    # Suggested topics
    st.markdown("**Suggested Topics:**")
    suggested_topics = [
        "Mutual Funds", "Personal Finance Basics", "Investment Strategies",
        "Retirement Planning", "Tax Planning", "Insurance Planning", "Credit Management"
    ]
    
    cols = st.columns(4)
    for i, suggested_topic in enumerate(suggested_topics):
        with cols[i % 4]:
            if st.button(suggested_topic, key=f"topic_{i}"):
                topic = suggested_topic
                st.rerun()
    
    # Generation options
    with st.expander("Advanced Options"):
        search_depth = st.selectbox(
            "Search Depth:",
            ["standard", "comprehensive"],
            index=0,
            help="Standard: Basic research, Comprehensive: Detailed research with more sources"
        )
        
        target_length = st.slider(
            "Target Word Count:",
            min_value=2000,
            max_value=8000,
            value=3000,
            step=500
        )
    
    # Generate button
    if st.button("Generate Learning Module", type="primary", disabled=not topic):
        if topic:
            with st.spinner("Creating your personalized learning module... This may take a few minutes."):
                try:
                    from Handout_Creator import FinBotHandoutCreator
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Initialize creator
                    status_text.text("Initializing AI agents...")
                    progress_bar.progress(20)
                    creator = FinBotHandoutCreator()
                    
                    # Create handout
                    status_text.text("Generating handout...")
                    progress_bar.progress(50)
                    result = creator.create_handout(topic)
                    progress_bar.progress(100)
                    
                    # Display success
                    status_text.text("Generation completed!")
                    st.success("Learning module created successfully!")
                    
                    # Display the handout content
                    st.markdown("### Generated Learning Module")
                    
                    # Download button
                    handout_content = result.get('handout_content', '')
                    if handout_content:
                        st.download_button(
                            label="Download as Markdown",
                            data=handout_content,
                            file_name=f"{topic.replace(' ', '_')}_handout.md",
                            mime="text/markdown"
                        )
                        
                        # Display content in expandable sections
                        st.markdown(handout_content)
                    
                except Exception as e:
                    st.error(f"Error creating learning module: {str(e)}")
                    st.exception(e)

def show_document_chat_page():
    """Display the document chat interface (placeholder)."""
    
    # Back to home button
    if st.button("Back to Home"):
        st.session_state.current_page = "home"
        st.rerun()
    
    st.markdown("## Chat with Your Document")
    st.info("This feature is coming soon! You'll be able to upload financial documents and chat with them.")
    
    # Placeholder UI
    uploaded_file = st.file_uploader(
        "Upload a financial document",
        type=['pdf', 'txt', 'docx'],
        disabled=True
    )
    
    st.markdown("### What you'll be able to do:")
    st.markdown("""
    - Upload PDFs, Word documents, or text files
    - Ask questions about the document content
    - Get summaries and key insights
    - Extract specific information
    - Compare multiple documents
    """)

# Run Streamlit app
if __name__ == "__main__":
    main_streamlit()
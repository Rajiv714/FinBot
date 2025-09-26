#!/usr/bin/env python3
"""
FinBot - Financial Literacy Chatbot
Main orchestration file for the RAG-based financial Q&A chatbot.
"""

import os
import sys
import logging
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from rag_pipeline import create_rag_pipeline
from document_parser import DocumentParser

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FinBot:
    """Main FinBot application class."""
    
    def __init__(self):
        """Initialize FinBot with RAG pipeline."""
        self.rag_pipeline = None
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize the RAG pipeline."""
        try:
            logger.info("Initializing FinBot RAG pipeline...")
            self.rag_pipeline = create_rag_pipeline()
            logger.info("FinBot initialized successfully!")
        except Exception as e:
            logger.error(f"Failed to initialize FinBot: {str(e)}")
            self.rag_pipeline = None
    
    def query(self, question: str, **kwargs) -> dict:
        """Process a single query."""
        if not self.rag_pipeline:
            return {
                "answer": "Sorry, the system is not properly initialized. Please check the logs.",
                "sources": [],
                "context_used": False
            }
        
        return self.rag_pipeline.query(question, **kwargs)
    
    def chat(self, messages: list, **kwargs) -> dict:
        """Process a chat conversation."""
        if not self.rag_pipeline:
            return {
                "answer": "Sorry, the system is not properly initialized. Please check the logs.",
                "sources": [],
                "context_used": False
            }
        
        return self.rag_pipeline.chat(messages, **kwargs)
    
    def get_status(self) -> dict:
        """Get system status."""
        if not self.rag_pipeline:
            return {"status": "error", "message": "Pipeline not initialized"}
        
        return self.rag_pipeline.get_system_status()


def create_streamlit_app():
    """Create Streamlit web interface."""
    
    st.set_page_config(
        page_title="FinBot - Financial Literacy Assistant",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .chat-message {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 10px;
        }
        .user-message {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        .bot-message {
            background-color: #f1f8e9;
            border-left: 4px solid #4caf50;
        }
        .source-info {
            font-size: 0.8rem;
            color: #666;
            margin-top: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">💰 FinBot - Your Financial Literacy Assistant</h1>', 
                unsafe_allow_html=True)
    
    # Initialize FinBot (with caching)
    @st.cache_resource
    def get_finbot():
        return FinBot()
    
    finbot = get_finbot()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Temperature control
        temperature = st.slider(
            "Response Creativity",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1,
            help="Lower values make responses more focused and consistent"
        )
        
        # Context settings
        include_context = st.checkbox(
            "Use Document Context",
            value=True,
            help="Include relevant information from financial documents"
        )
        
        # System status
        st.header("📊 System Status")
        if st.button("Check Status"):
            with st.spinner("Checking system status..."):
                status = finbot.get_status()
                if status.get("status") == "healthy":
                    st.success("✅ System is healthy")
                    with st.expander("Detailed Status"):
                        st.json(status)
                else:
                    st.error("❌ System issues detected")
                    st.error(status.get("error", "Unknown error"))
        
        # Quick examples
        st.header("💡 Try These Questions")
        example_questions = [
            "What is compound interest?",
            "How should I start investing?",
            "What's the difference between stocks and bonds?",
            "How do I create a budget?",
            "What is diversification in investing?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{question}"):
                st.session_state.current_question = question
    
    # Main chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "current_question" in st.session_state:
        st.session_state.messages.append({
            "role": "user",
            "content": st.session_state.current_question
        })
        del st.session_state.current_question
    
    # Display chat history
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(
                f'<div class="chat-message user-message"><strong>You:</strong><br>{content}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-message bot-message"><strong>FinBot:</strong><br>{content}</div>',
                unsafe_allow_html=True
            )
            
            # Show sources if available
            if "sources" in message and message["sources"]:
                with st.expander(f"📚 Sources ({len(message['sources'])} documents)"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**Source {i}** (Relevance: {source['score']:.2f})")
                        st.markdown(f"*{source['metadata'].get('filename', 'Unknown')}*")
                        st.text(source['text'])
                        st.markdown("---")
    
    # Chat input
    question = st.chat_input("Ask me anything about financial literacy...")
    
    if question:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": question
        })
        
        # Generate response
        with st.spinner("Thinking... 🤔"):
            try:
                response_data = finbot.chat(
                    messages=st.session_state.messages,
                    include_context=include_context,
                    temperature=temperature
                )
                
                answer = response_data.get("answer", "I couldn't generate a response.")
                sources = response_data.get("sources", [])
                
                # Add bot response
                bot_message = {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                }
                st.session_state.messages.append(bot_message)
                
                # Rerun to display new messages
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"Error processing question: {str(e)}")


def run_cli():
    """Run FinBot in command line interface mode."""
    print("🤖 FinBot - Financial Literacy Assistant")
    print("=" * 50)
    print("Ask me anything about financial literacy! Type 'quit' to exit.\n")
    
    # Initialize FinBot
    finbot = FinBot()
    if not finbot.rag_pipeline:
        print("❌ Failed to initialize FinBot. Please check your configuration.")
        return
    
    # Chat loop
    messages = []
    while True:
        try:
            question = input("\n💬 You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Goodbye! Thanks for using FinBot!")
                break
            
            if not question:
                continue
            
            messages.append({"role": "user", "content": question})
            
            print("\n🤖 FinBot: ", end="", flush=True)
            
            # Get response
            response_data = finbot.chat(messages)
            answer = response_data.get("answer", "I couldn't generate a response.")
            sources = response_data.get("sources", [])
            
            print(answer)
            
            # Show sources if available
            if sources:
                print(f"\n📚 Sources ({len(sources)} documents found):")
                for i, source in enumerate(sources, 1):
                    filename = source['metadata'].get('filename', 'Unknown')
                    score = source['score']
                    print(f"  {i}. {filename} (relevance: {score:.2f})")
            
            messages.append({"role": "assistant", "content": answer})
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using FinBot!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            logger.error(f"CLI error: {str(e)}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="FinBot - Financial Literacy Assistant")
    parser.add_argument(
        "--mode",
        choices=["web", "cli"],
        default="web",
        help="Run mode: web (Streamlit) or cli (command line)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "web":
        create_streamlit_app()
    else:
        run_cli()


if __name__ == "__main__":
    main()
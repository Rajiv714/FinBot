#!/usr/bin/env python3
"""
FinBot - Simple Financial Literacy Chatbot
Main file for the RAG-based financial Q&A chatbot.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from rag_pipeline import create_rag_pipeline
except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure all dependencies are installed and the model files are available.")
    sys.exit(1)


class FinBot:
    """Simple FinBot application class."""
    
    def __init__(self):
        """Initialize FinBot with RAG pipeline."""
        try:
            self.rag_pipeline = create_rag_pipeline()
            print("FinBot initialized successfully!")
        except Exception as e:
            print(f"Failed to initialize FinBot: {str(e)}")
            self.rag_pipeline = None
    
    def query(self, question: str, **kwargs) -> dict:
        """Process a single query."""
        if not self.rag_pipeline:
            return {
                "answer": "Sorry, the system is not properly initialized.",
                "sources": [],
                "context_used": False
            }
        
        return self.rag_pipeline.query(question, **kwargs)
    
    def chat(self, messages: list, **kwargs) -> dict:
        """Process a chat conversation."""
        if not self.rag_pipeline:
            return {
                "answer": "Sorry, the system is not properly initialized.",
                "sources": [],
                "context_used": False
            }
        
        return self.rag_pipeline.chat(messages, **kwargs)
    
    def get_status(self) -> dict:
        """Get system status."""
        if not self.rag_pipeline:
            return {"status": "error", "message": "Pipeline not initialized"}
        
        return self.rag_pipeline.get_system_status()


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


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="FinBot - Financial Literacy Assistant")
    parser.add_argument(
        "--query",
        help="Ask a single question and exit"
    )
    
    args = parser.parse_args()
    
    if args.query:
        # Single query mode
        finbot = FinBot()
        if finbot.rag_pipeline:
            response = finbot.query(args.query)
            print(f"Question: {args.query}")
            print(f"Answer: {response['answer']}")
            if response.get('sources'):
                print(f"Sources: {len(response['sources'])} documents")
        else:
            print("Failed to initialize FinBot")
    else:
        # Interactive CLI mode
        run_cli()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
FinBot - Simple Financial Literacy Chatbot
Main file for the RAG-based financial Q&A chatbot.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from chatbot import create_finbot_chatbot
except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure all dependencies are installed.")
    sys.exit(1)


def main():
    """Main entry point."""
    print("🤖 FinBot - Financial Literacy Assistant")
    print("=" * 50)
    print("Ask me anything about financial literacy! Type 'quit' to exit.\n")
    
    # Initialize FinBot
    finbot = create_finbot_chatbot()
    if not finbot.rag_pipeline:
        print("❌ Failed to initialize FinBot. Please check your configuration.")
        return
    
    # Chat loop
    while True:
        try:
            question = input("\n💬 You: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Goodbye! Thanks for using FinBot!")
                break
            
            if not question:
                continue
            
            print("\n🤖 FinBot: ", end="", flush=True)
            
            # Get response
            response_data = finbot.chat(question)
            answer = response_data.get("answer", "I couldn't generate a response.")
            
            print(answer)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using FinBot!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
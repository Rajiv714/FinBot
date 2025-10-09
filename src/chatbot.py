"""
FinBot Chatbot - Simple Financial Assistant
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from rag_pipeline import create_rag_pipeline


class FinBotChatbot:
    """Simple FinBot chatbot."""
    
    def __init__(self):
        """Initialize the chatbot."""
        try:
            self.rag_pipeline = create_rag_pipeline()
            self.conversation_history = []
        except Exception as e:
            print(f"Failed to initialize FinBot: {str(e)}")
            self.rag_pipeline = None
    
    def chat(self, message: str) -> Dict[str, Any]:
        """Chat with the bot."""
        if not self.rag_pipeline:
            return {"answer": "Sorry, the system is not initialized."}
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Get response
        response = self.rag_pipeline.chat(self.conversation_history)
        
        # Add response to history
        if response.get("answer"):
            self.conversation_history.append({"role": "assistant", "content": response["answer"]})
        
        return response


def create_finbot_chatbot() -> FinBotChatbot:
    """Create a FinBot chatbot instance."""
    return FinBotChatbot()
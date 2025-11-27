"""
Chatbot service - Business logic for RAG-based Q&A
"""
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src directory to path
src_path = str(Path(__file__).parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from rag_pipeline import create_rag_pipeline


class ChatbotService:
    """Service for chatbot interactions"""
    
    def __init__(self):
        """Initialize chatbot service with RAG pipeline"""
        self.pipeline = create_rag_pipeline()
    
    def chat_query(
        self,
        query: str,
        include_context: bool = True,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process a single query using RAG.
        
        Args:
            query: User's question
            include_context: Whether to use retrieved context
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity score
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            result = self.pipeline.query(
                question=query,
                top_k=top_k,
                score_threshold=score_threshold,
                include_context=include_context
            )
            
            return {
                "success": True,
                "answer": result["answer"],
                "sources": result.get("sources", []),
                "context_used": result.get("context_used", False)
            }
            
        except Exception as e:
            return {
                "success": False,
                "answer": f"I apologize, but I encountered an error: {str(e)}",
                "sources": [],
                "context_used": False,
                "error": str(e)
            }
    
    def chat_with_history(
        self,
        messages: List[Dict[str, str]],
        include_context: bool = True,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process chat with conversation history.
        
        Args:
            messages: List of chat messages with 'role' and 'content'
            include_context: Whether to use retrieved context
            top_k: Number of documents to retrieve
            score_threshold: Minimum similarity score
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            result = self.pipeline.chat(
                messages=messages,
                top_k=top_k,
                score_threshold=score_threshold,
                include_context=include_context
            )
            
            return {
                "success": True,
                "answer": result["answer"],
                "sources": result.get("sources", []),
                "context_used": result.get("context_used", False)
            }
            
        except Exception as e:
            return {
                "success": False,
                "answer": f"I apologize, but I encountered an error: {str(e)}",
                "sources": [],
                "context_used": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get system status and health.
        
        Returns:
            Dictionary with system status information
        """
        try:
            status = self.pipeline.get_system_status()
            
            # Extract key information
            vector_db_info = status.get("vector_db", {}).get("collection_info", {})
            
            return {
                "status": status.get("status", "unknown"),
                "vector_db_healthy": status.get("vector_db", {}).get("healthy", False),
                "vector_db_documents": vector_db_info.get("vectors_count", 0),
                "llm_configured": status.get("llm_service", {}).get("api_configured", False),
                "embedding_model": status.get("embedding_service", {}).get("model", "unknown"),
                "components": status
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "vector_db_healthy": False,
                "vector_db_documents": 0,
                "llm_configured": False,
                "embedding_model": "unknown",
                "components": {}
            }


# Global service instance
_chatbot_service = None


def get_chatbot_service() -> ChatbotService:
    """Get or create chatbot service singleton"""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
    return _chatbot_service

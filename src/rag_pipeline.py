"""
Simple RAG pipeline that orchestrates document retrieval and response generation.
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add current directory to path to ensure imports work
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from embeddings.embeddings import create_embedding_service
from vectorstore.qdrant_client import create_qdrant_client
from llm.gemini import create_gemini_service


class RAGPipeline:
    """Simple RAG pipeline for financial document Q&A."""
    
    def __init__(self):
        """Initialize the RAG pipeline with all components."""
        # Load default configuration from environment
        self.default_top_k = int(os.getenv("TOP_K_RESULTS", "5"))
        self.default_score_threshold = float(os.getenv("SCORE_THRESHOLD", "0.3"))
        
        # Initialize embedding service
        self.embedding_service = create_embedding_service()
        
        # Get embedding dimension and create vector DB
        embedding_dim = self.embedding_service.get_embedding_dimension()
        self.vector_db = create_qdrant_client(vector_size=embedding_dim)
        
        # Initialize Gemini LLM service for chat (shorter, faster responses)
        self.llm_service = create_gemini_service(use_case="chat")
    
    def _get_retrieval_params(self, top_k: Optional[int], score_threshold: Optional[float]) -> tuple:
        """Get retrieval parameters with fallback to defaults."""
        effective_top_k = top_k if top_k is not None else self.default_top_k
        effective_score_threshold = score_threshold if score_threshold is not None else self.default_score_threshold
        return effective_top_k, effective_score_threshold
    
    def _retrieve_context(self, query: str, top_k: int, score_threshold: float) -> tuple:
        """Retrieve relevant context for a query."""
        sources = []
        context = ""
        
        # Generate query embedding
        query_embedding = self.embedding_service.encode([query])[0]
        
        # Retrieve similar documents
        search_results = self.vector_db.search(
            query_embedding=query_embedding,
            limit=top_k,
            score_threshold=score_threshold
        )
        
        # Format context and sources
        if search_results:
            context_parts = []
            
            for result in search_results:
                chunk_text = result["text"]
                context_parts.append(chunk_text)
                
                sources.append({
                    "text": chunk_text[:500] + "..." if len(chunk_text) > 500 else chunk_text,
                    "score": result["score"],
                    "metadata": result["metadata"]
                })
            
            context = "\n\n".join(context_parts)
        
        return context, sources
    
    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        include_context: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a single query using RAG.
        
        Args:
            question: User question
            top_k: Number of similar documents to retrieve
            score_threshold: Minimum similarity score for retrieval
            include_context: Whether to include retrieved context in response
            **kwargs: Additional arguments for LLM generation
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            effective_top_k, effective_score_threshold = self._get_retrieval_params(top_k, score_threshold)
            
            sources = []
            context = ""
            
            if include_context:
                context, sources = self._retrieve_context(question, effective_top_k, effective_score_threshold)
            
            # Generate response using LLM (use query/context interface, not prompt)
            answer = self.llm_service.generate_response(
                query=question,
                context=context if context else None,
                **kwargs
            )
            
            return {
                "answer": answer,
                "sources": sources,
                "context_used": bool(context),
                "question": question
            }
            
        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error: {str(e)}",
                "sources": [],
                "context_used": False,
                "question": question,
                "error": str(e)
            }
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        include_context: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a chat conversation using RAG.
        NO HISTORY SENT TO LLM - Only current question to save tokens.
        
        Args:
            messages: List of chat messages
            top_k: Number of similar documents to retrieve
            score_threshold: Minimum similarity score for retrieval
            include_context: Whether to include retrieved context
            **kwargs: Additional arguments for LLM generation
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            effective_top_k, effective_score_threshold = self._get_retrieval_params(top_k, score_threshold)
            
            # Get the last user message as the query
            last_message = None
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_message = msg.get("content", "")
                    break
            
            if not last_message:
                return {
                    "answer": "I didn't receive a question. Please ask me something about financial topics.",
                    "sources": [],
                    "context_used": False
                }
            
            # SIMPLIFIED: Just use the query method instead of sending full history
            # This saves tokens by not sending conversation history to Gemini
            result = self.query(
                question=last_message,
                top_k=effective_top_k,
                score_threshold=effective_score_threshold,
                include_context=include_context,
                **kwargs
            )
            
            return {
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "context_used": result.get("context_used", False),
                "messages": messages
            }
            
        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error: {str(e)}",
                "sources": [],
                "context_used": False,
                "messages": messages,
                "error": str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the status of all system components."""
        try:
            # Check vector database
            vector_db_info = self.vector_db.get_collection_info()
            vector_db_healthy = self.vector_db.health_check()
            
            # Check embedding service
            embedding_dim = self.embedding_service.get_embedding_dimension()
            
            return {
                "status": "healthy",
                "vector_db": {
                    "healthy": vector_db_healthy,
                    "collection_info": vector_db_info,
                },
                "embedding_service": {
                    "model": self.embedding_service.model_name,
                    "dimension": embedding_dim
                },
                "llm_service": {
                    "model_name": self.llm_service.model_name,
                    "api_configured": bool(self.llm_service.api_key),
                    "temperature": self.llm_service.temperature,
                    "max_tokens": self.llm_service.max_tokens
                },
                "configuration": {
                    "chunk_size": int(os.getenv("CHUNK_SIZE", "1000")),
                    "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "200")),
                    "top_k_results": self.default_top_k,
                    "score_threshold": self.default_score_threshold
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


def create_rag_pipeline() -> RAGPipeline:
    """
    Factory function to create a RAG pipeline.
    
    Returns:
        Configured RAGPipeline instance
    """
    return RAGPipeline()
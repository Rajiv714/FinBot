"""
Simple RAG pipeline that orchestrates document retrieval and response generation.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add current directory to path to ensure imports work
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from embeddings.qwen import create_embedding_service
from vectorstore.qdrant_client import create_qdrant_client
from llm.llama import create_llama_service


class RAGPipeline:
    """Simple RAG pipeline for financial document Q&A."""
    
    def __init__(self):
        """Initialize the RAG pipeline with all components."""
        # Initialize embedding service
        self.embedding_service = create_embedding_service()
        
        # Get embedding dimension and create vector DB
        embedding_dim = self.embedding_service.get_embedding_dimension()
        self.vector_db = create_qdrant_client(vector_size=embedding_dim)
        
        # Initialize LLM service
        self.llm_service = create_llama_service()
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
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
            sources = []
            context = ""
            
            if include_context:
                # Generate query embedding
                query_embedding = self.embedding_service.encode([question])[0]
                
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
                        context_parts.append(result["text"])
                        sources.append({
                            "text": result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"],
                            "score": result["score"],
                            "metadata": result["metadata"]
                        })
                    
                    context = "\n\n".join(context_parts)
            
            # Generate response using LLM
            answer = self.llm_service.generate_response(
                prompt=question,
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
        top_k: int = 5,
        score_threshold: float = 0.3,
        include_context: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a chat conversation using RAG.
        
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
            
            sources = []
            enhanced_messages = messages.copy()
            
            if include_context:
                # Generate query embedding for the last user message
                query_embedding = self.embedding_service.encode([last_message])[0]
                
                # Retrieve similar documents
                search_results = self.vector_db.search(
                    query_embedding=query_embedding,
                    limit=top_k,
                    score_threshold=score_threshold
                )
                
                # Add context to the conversation if we found relevant documents
                if search_results:
                    context_parts = []
                    for result in search_results:
                        context_parts.append(result["text"])
                        sources.append({
                            "text": result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"],
                            "score": result["score"],
                            "metadata": result["metadata"]
                        })
                    
                    context = "\n\n".join(context_parts)
                    
                    # Insert context before the last user message
                    enhanced_messages[-1]["content"] = f"Context from financial documents:\n{context}\n\nQuestion: {last_message}"
            
            # Generate response using chat format
            answer = self.llm_service.chat(enhanced_messages, **kwargs)
            
            return {
                "answer": answer,
                "sources": sources,
                "context_used": bool(sources),
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
                    "model_path": self.llm_service.model_path,
                    "device": self.llm_service.device
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
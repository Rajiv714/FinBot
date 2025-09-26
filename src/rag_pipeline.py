"""
Retrieval-Augmented Generation (RAG) pipeline for financial Q&A chatbot.
Combines vector similarity search with LLM generation.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dotenv import load_dotenv

from .document_parser import DocumentParser
from .embedding_service import EmbeddingService, create_embedding_service
from .vectordb import QdrantVectorDB, create_qdrant_client
from .llm import LlamaLLMService, create_llama_service

# Load environment variables
load_dotenv()


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for financial chatbot."""
    
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_db: Optional[QdrantVectorDB] = None,
        llm_service: Optional[LlamaLLMService] = None,
        top_k: int = 5,
        score_threshold: float = 0.7
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            embedding_service: Service for generating embeddings
            vector_db: Vector database client
            llm_service: Large language model service
            top_k: Number of top documents to retrieve
            score_threshold: Minimum similarity score for retrieval
        """
        self.logger = logging.getLogger(__name__)
        self.top_k = int(os.getenv("TOP_K", str(top_k)))
        self.score_threshold = score_threshold
        
        # Initialize services
        self.embedding_service = embedding_service or create_embedding_service()
        self.llm_service = llm_service or create_llama_service()
        
        # Initialize vector DB with correct embedding dimension
        embedding_dim = self.embedding_service.get_embedding_dimension()
        self.vector_db = vector_db or create_qdrant_client(vector_size=embedding_dim)
        
        # Update vector DB dimension if needed
        try:
            collection_info = self.vector_db.get_collection_info()
            if collection_info.get("vector_size", 0) != embedding_dim:
                self.logger.info(f"Updating vector DB dimension to {embedding_dim}")
                self.vector_db.update_vector_size(embedding_dim)
        except Exception as e:
            self.logger.warning(f"Could not verify vector dimension: {e}")
        
        self.logger.info("RAG pipeline initialized successfully")
    
    def query(
        self,
        question: str,
        include_context: bool = True,
        max_context_length: int = 2000,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the RAG pipeline.
        
        Args:
            question: User question
            include_context: Whether to include retrieved context
            max_context_length: Maximum length of context to include
            temperature: Override temperature for generation
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            self.logger.info(f"Processing query: {question[:100]}...")
            
            # Step 1: Generate query embedding
            query_embedding = self.embedding_service.encode(question)
            
            # Step 2: Retrieve relevant documents
            retrieved_docs = []
            if include_context:
                retrieved_docs = self.vector_db.search(
                    query_embedding=query_embedding,
                    limit=self.top_k,
                    score_threshold=self.score_threshold
                )
            
            # Step 3: Prepare context
            context = self._prepare_context(retrieved_docs, max_context_length)
            
            # Step 4: Generate response
            response = self.llm_service.generate_response(
                prompt=question,
                context=context if include_context else None,
                temperature=temperature
            )
            
            # Step 5: Prepare result
            result = {
                "question": question,
                "answer": response,
                "sources": [
                    {
                        "text": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"],
                        "score": doc["score"],
                        "metadata": doc["metadata"]
                    }
                    for doc in retrieved_docs
                ],
                "context_used": context is not None and len(context) > 0,
                "num_sources": len(retrieved_docs)
            }
            
            self.logger.info(f"Generated response with {len(retrieved_docs)} sources")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return {
                "question": question,
                "answer": "I apologize, but I encountered an error while processing your question. Please try again.",
                "sources": [],
                "context_used": False,
                "num_sources": 0,
                "error": str(e)
            }
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        include_context: bool = True,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process a chat conversation through the RAG pipeline.
        
        Args:
            messages: List of messages in chat format
            include_context: Whether to include retrieved context
            temperature: Override temperature for generation
            
        Returns:
            Dictionary with response and metadata
        """
        # Extract the latest user message for context retrieval
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        if not user_messages:
            return {
                "answer": "I didn't receive a question. Please ask me something about financial literacy.",
                "sources": [],
                "context_used": False
            }
        
        latest_question = user_messages[-1].get("content", "")
        
        # Get context for the latest question
        context = ""
        retrieved_docs = []
        
        if include_context and latest_question:
            query_embedding = self.embedding_service.encode(latest_question)
            retrieved_docs = self.vector_db.search(
                query_embedding=query_embedding,
                limit=self.top_k,
                score_threshold=self.score_threshold
            )
            context = self._prepare_context(retrieved_docs, max_context_length=1500)
        
        # Enhance the latest message with context
        if context and include_context:
            enhanced_messages = messages.copy()
            enhanced_messages[-1] = {
                "role": "user",
                "content": f"Context from financial documents:\n{context}\n\nQuestion: {latest_question}"
            }
        else:
            enhanced_messages = messages
        
        # Generate response
        try:
            response = self.llm_service.chat(
                messages=enhanced_messages,
                temperature=temperature
            )
            
            return {
                "answer": response,
                "sources": [
                    {
                        "text": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"],
                        "score": doc["score"],
                        "metadata": doc["metadata"]
                    }
                    for doc in retrieved_docs
                ],
                "context_used": len(context) > 0,
                "num_sources": len(retrieved_docs)
            }
            
        except Exception as e:
            self.logger.error(f"Error in chat processing: {str(e)}")
            return {
                "answer": "I apologize, but I encountered an error. Please try rephrasing your question.",
                "sources": [],
                "context_used": False,
                "error": str(e)
            }
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> Dict[str, Any]:
        """
        Add documents to the knowledge base.
        
        Args:
            documents: List of document dictionaries with 'content' and 'metadata'
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Summary of the addition process
        """
        try:
            self.logger.info(f"Adding {len(documents)} documents to knowledge base")
            
            # Initialize document parser for chunking
            parser = DocumentParser()
            
            all_chunks = []
            all_embeddings = []
            all_metadata = []
            
            for doc in documents:
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                
                if not content:
                    continue
                
                # Chunk the document
                chunks = parser.chunk_text(
                    text=content,
                    chunk_size=chunk_size,
                    overlap=chunk_overlap
                )
                
                # Process each chunk
                for chunk in chunks:
                    chunk_text = chunk["text"]
                    chunk_metadata = metadata.copy()
                    chunk_metadata.update({
                        "chunk_id": chunk["chunk_id"],
                        "start_word": chunk["start_word"],
                        "end_word": chunk["end_word"]
                    })
                    
                    all_chunks.append(chunk_text)
                    all_metadata.append(chunk_metadata)
            
            if not all_chunks:
                return {"status": "error", "message": "No valid chunks found"}
            
            # Generate embeddings for all chunks
            self.logger.info(f"Generating embeddings for {len(all_chunks)} chunks")
            embeddings = self.embedding_service.encode(all_chunks)
            
            # Add to vector database
            document_ids = self.vector_db.add_documents(
                texts=all_chunks,
                embeddings=embeddings,
                metadatas=all_metadata
            )
            
            return {
                "status": "success",
                "documents_processed": len(documents),
                "chunks_created": len(all_chunks),
                "embeddings_generated": len(embeddings),
                "document_ids": document_ids
            }
            
        except Exception as e:
            self.logger.error(f"Error adding documents: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "documents_processed": 0,
                "chunks_created": 0
            }
    
    def _prepare_context(
        self,
        retrieved_docs: List[Dict[str, Any]],
        max_length: int = 2000
    ) -> str:
        """
        Prepare context string from retrieved documents.
        
        Args:
            retrieved_docs: List of retrieved document chunks
            max_length: Maximum length of context
            
        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return ""
        
        context_parts = []
        current_length = 0
        
        for doc in retrieved_docs:
            text = doc.get("text", "")
            source = doc.get("metadata", {}).get("filename", "Unknown source")
            score = doc.get("score", 0.0)
            
            # Format the chunk with source info
            formatted_chunk = f"[Source: {source} (Relevance: {score:.2f})]\n{text}"
            
            # Check if adding this chunk would exceed max length
            if current_length + len(formatted_chunk) > max_length:
                # Truncate the current chunk if it's the first one
                if not context_parts:
                    remaining_space = max_length - current_length - 50  # Leave some buffer
                    if remaining_space > 100:  # Only add if meaningful content can fit
                        truncated_chunk = formatted_chunk[:remaining_space] + "..."
                        context_parts.append(truncated_chunk)
                break
            
            context_parts.append(formatted_chunk)
            current_length += len(formatted_chunk) + 2  # +2 for separating newlines
        
        return "\n\n".join(context_parts)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all system components."""
        try:
            # Check vector DB
            vectordb_healthy = self.vector_db.health_check()
            collection_info = self.vector_db.get_collection_info()
            
            # Get model info
            llm_info = self.llm_service.get_model_info()
            embedding_dim = self.embedding_service.get_embedding_dimension()
            
            return {
                "status": "healthy" if vectordb_healthy else "degraded",
                "vector_db": {
                    "healthy": vectordb_healthy,
                    "collection_info": collection_info
                },
                "llm_service": llm_info,
                "embedding_service": {
                    "model_name": self.embedding_service.model_name,
                    "dimension": embedding_dim,
                    "device": self.embedding_service.device
                },
                "config": {
                    "top_k": self.top_k,
                    "score_threshold": self.score_threshold
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


def create_rag_pipeline(
    embedding_model_name: Optional[str] = None,
    llm_model_path: Optional[str] = None,
    qdrant_host: Optional[str] = None,
    qdrant_port: Optional[int] = None
) -> RAGPipeline:
    """
    Factory function to create RAG pipeline with environment configurations.
    
    Args:
        embedding_model_name: Override embedding model name
        llm_model_path: Override LLM model path
        qdrant_host: Override Qdrant host
        qdrant_port: Override Qdrant port
        
    Returns:
        Configured RAGPipeline instance
    """
    # Create services with environment variables or overrides
    embedding_service = create_embedding_service(model_name=embedding_model_name)
    llm_service = create_llama_service(model_path=llm_model_path)
    
    embedding_dim = embedding_service.get_embedding_dimension()
    vector_db = create_qdrant_client(
        host=qdrant_host,
        port=qdrant_port,
        vector_size=embedding_dim
    )
    
    return RAGPipeline(
        embedding_service=embedding_service,
        vector_db=vector_db,
        llm_service=llm_service
    )
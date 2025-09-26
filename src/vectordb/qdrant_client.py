"""
Qdrant vector database client for storing and searching document embeddings.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import (
    Distance, VectorParams, CreateCollection,
    PointStruct, ScoredPoint, SearchRequest
)
import uuid


class QdrantVectorDB:
    """Client for Qdrant vector database operations."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "financial_documents",
        vector_size: int = 1024  # Default for many embedding models
    ):
        """
        Initialize Qdrant client.
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
            collection_name: Name of the collection to use
            vector_size: Size of embedding vectors
        """
        self.logger = logging.getLogger(__name__)
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Initialize client
        self.client = QdrantClient(host=host, port=port)
        self.logger.info(f"Connected to Qdrant at {host}:{port}")
        
        # Create collection if it doesn't exist
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                self.logger.info(f"Collection '{self.collection_name}' created successfully")
            else:
                self.logger.info(f"Collection '{self.collection_name}' already exists")
                
        except Exception as e:
            self.logger.error(f"Error ensuring collection exists: {str(e)}")
            raise
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: np.ndarray,
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector database.
        
        Args:
            texts: List of text chunks
            embeddings: Embedding vectors for the texts
            metadatas: Metadata for each text chunk
            ids: Optional custom IDs (generated if not provided)
            
        Returns:
            List of document IDs
        """
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        
        if len(texts) != len(embeddings) or len(texts) != len(metadatas):
            raise ValueError("texts, embeddings, and metadatas must have the same length")
        
        points = []
        for i, (text, embedding, metadata, doc_id) in enumerate(zip(texts, embeddings, metadatas, ids)):
            # Add text to metadata
            full_metadata = metadata.copy()
            full_metadata["text"] = text
            
            point = PointStruct(
                id=doc_id,
                vector=embedding.tolist(),
                payload=full_metadata
            )
            points.append(point)
        
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            self.logger.info(f"Added {len(points)} documents to collection")
            return ids
            
        except Exception as e:
            self.logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def search(
        self,
        query_embedding: np.ndarray,
        limit: int = 5,
        score_threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold
            filters: Optional metadata filters
            
        Returns:
            List of search results with text, metadata, and scores
        """
        try:
            # Prepare search request
            search_params = {
                "collection_name": self.collection_name,
                "query_vector": query_embedding.tolist(),
                "limit": limit,
                "with_payload": True,
                "with_vectors": False
            }
            
            # Add score threshold if provided
            if score_threshold is not None:
                search_params["score_threshold"] = score_threshold
            
            # Add filters if provided
            if filters:
                search_params["query_filter"] = self._build_filter(filters)
            
            results = self.client.search(**search_params)
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_result = {
                    "id": result.id,
                    "text": result.payload.get("text", ""),
                    "score": result.score,
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"}
                }
                formatted_results.append(formatted_result)
            
            self.logger.debug(f"Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error searching documents: {str(e)}")
            raise
    
    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents by IDs.
        
        Args:
            ids: List of document IDs to delete
            
        Returns:
            True if successful
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=ids
                )
            )
            self.logger.info(f"Deleted {len(ids)} documents")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting documents: {str(e)}")
            return False
    
    def update_vector_size(self, new_size: int):
        """
        Update the vector size and recreate collection if needed.
        
        Args:
            new_size: New vector size
        """
        if new_size != self.vector_size:
            self.logger.info(f"Updating vector size from {self.vector_size} to {new_size}")
            self.vector_size = new_size
            
            # Delete and recreate collection with new vector size
            try:
                self.client.delete_collection(collection_name=self.collection_name)
                self._ensure_collection_exists()
                self.logger.info("Collection recreated with new vector size")
            except Exception as e:
                self.logger.error(f"Error updating vector size: {str(e)}")
                raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": info.config.name,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            self.logger.error(f"Error getting collection info: {str(e)}")
            return {}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            # Delete all points
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter()
                )
            )
            self.logger.info("Collection cleared successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing collection: {str(e)}")
            return False
    
    def _build_filter(self, filters: Dict[str, Any]) -> models.Filter:
        """Build Qdrant filter from dictionary."""
        conditions = []
        
        for key, value in filters.items():
            if isinstance(value, str):
                condition = models.FieldCondition(
                    key=key,
                    match=models.MatchValue(value=value)
                )
            elif isinstance(value, (int, float)):
                condition = models.FieldCondition(
                    key=key,
                    match=models.MatchValue(value=value)
                )
            elif isinstance(value, list):
                condition = models.FieldCondition(
                    key=key,
                    match=models.MatchAny(any=value)
                )
            else:
                continue  # Skip unsupported filter types
            
            conditions.append(condition)
        
        if conditions:
            return models.Filter(must=conditions)
        else:
            return models.Filter()
    
    def health_check(self) -> bool:
        """Check if Qdrant is healthy and accessible."""
        try:
            collections = self.client.get_collections()
            self.logger.info("Qdrant health check passed")
            return True
        except Exception as e:
            self.logger.error(f"Qdrant health check failed: {str(e)}")
            return False


def create_qdrant_client(
    host: Optional[str] = None,
    port: Optional[int] = None,
    collection_name: Optional[str] = None,
    vector_size: int = 1024
) -> QdrantVectorDB:
    """
    Factory function to create Qdrant client with environment variables.
    
    Args:
        host: Qdrant host (uses env variable if None)
        port: Qdrant port (uses env variable if None)  
        collection_name: Collection name (uses env variable if None)
        vector_size: Vector dimension
        
    Returns:
        Configured QdrantVectorDB instance
    """
    if host is None:
        host = os.getenv("QDRANT_HOST", "localhost")
    
    if port is None:
        port = int(os.getenv("QDRANT_PORT", "6333"))
    
    if collection_name is None:
        collection_name = os.getenv("QDRANT_COLLECTION_NAME", "financial_documents")
    
    return QdrantVectorDB(
        host=host,
        port=port,
        collection_name=collection_name,
        vector_size=vector_size
    )
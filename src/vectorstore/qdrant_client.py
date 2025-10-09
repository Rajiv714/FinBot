"""
Simple Qdrant vector database client.
"""

import os
from typing import List, Dict, Any, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import uuid


class QdrantVectorDB:
    """Simple Qdrant vector database client."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "financial_documents",
        vector_size: int = 1024  # Default for BAAI/bge-large-en-v1.5
    ):
        """
        Initialize Qdrant client.
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
            collection_name: Name of the collection to use
            vector_size: Size of embedding vectors
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Load default retrieval parameters
        self.default_top_k = int(os.getenv("TOP_K_RESULTS", "5"))
        self.default_score_threshold = float(os.getenv("SCORE_THRESHOLD", "0.3"))
        
        # Initialize client
        self.client = QdrantClient(host=host, port=port)
        
        # Create collection if it doesn't exist
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
            else:
                # Check if existing collection has the correct vector size
                collection_info = self.client.get_collection(collection_name=self.collection_name)
                existing_size = collection_info.config.params.vectors.size
                if existing_size != self.vector_size:
                    print(f"WARNING: Vector size mismatch: collection has {existing_size}, but model needs {self.vector_size}")
                    print(f"Recreating collection '{self.collection_name}' with correct dimensions...")
                    self._recreate_collection()
        except Exception as e:
            raise RuntimeError(f"Failed to create collection: {str(e)}")
    
    def _recreate_collection(self):
        """Delete and recreate the collection with correct vector size."""
        try:
            # Delete existing collection
            self.client.delete_collection(collection_name=self.collection_name)
            
            # Create new collection with correct vector size
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            print(f"SUCCESS: Collection '{self.collection_name}' recreated with vector size {self.vector_size}")
        except Exception as e:
            raise RuntimeError(f"Failed to recreate collection: {str(e)}")
    
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
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return ids
    
    def search(
        self,
        query_embedding: np.ndarray,
        limit: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of search results with text, metadata, and scores
        """
        # Use instance defaults if not provided
        effective_limit = limit if limit is not None else self.default_top_k
        effective_threshold = score_threshold if score_threshold is not None else self.default_score_threshold
        
        search_params = {
            "collection_name": self.collection_name,
            "query_vector": query_embedding.tolist(),
            "limit": effective_limit,
            "with_payload": True,
            "with_vectors": False
        }
        
        if effective_threshold is not None:
            search_params["score_threshold"] = effective_threshold
        
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
        
        return formatted_results
    
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
            return {"error": str(e)}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter()
                )
            )
            return True
        except Exception as e:
            return False
    
    def health_check(self) -> bool:
        """Check if Qdrant is healthy and accessible."""
        try:
            collections = self.client.get_collections()
            return True
        except Exception as e:
            return False


def create_qdrant_client(
    host: str = "localhost",
    port: int = 6333,
    collection_name: str = "financial_documents",
    vector_size: int = 1024  # Default for BAAI/bge-large-en-v1.5
) -> QdrantVectorDB:
    """
    Factory function to create Qdrant client.
    
    Args:
        host: Qdrant host
        port: Qdrant port
        collection_name: Collection name
        vector_size: Vector dimension
        
    Returns:
        Configured QdrantVectorDB instance
    """
    return QdrantVectorDB(
        host=host,
        port=port,
        collection_name=collection_name,
        vector_size=vector_size
    )
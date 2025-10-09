"""
Simple embedding service using SentenceTransformers.
"""

import os
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Simple embedding service using SentenceTransformers."""
    
    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5"):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the SentenceTransformer model
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for input texts.
        
        Args:
            texts: Single text string or list of text strings
            
        Returns:
            NumPy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        return self.model.get_sentence_embedding_dimension()
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score
        """
        if embedding1.ndim == 1:
            embedding1 = embedding1.reshape(1, -1)
        if embedding2.ndim == 1:
            embedding2 = embedding2.reshape(1, -1)
        
        similarity = np.dot(embedding1, embedding2.T)
        return float(similarity[0][0])


def create_embedding_service(model_name: str = None) -> EmbeddingService:
    """
    Factory function to create embedding service.
    
    Args:
        model_name: Model name (if None, uses environment variable)
        
    Returns:
        Configured EmbeddingService instance
    """
    if model_name is None:
        model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")
    return EmbeddingService(model_name=model_name)
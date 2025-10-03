"""
Embedding service for generating vector representations of text using Qwen2 embedding model.
"""

import os
from typing import List, Union, Optional
import logging
import torch
import numpy as np
from transformers import AutoModel, AutoTokenizer
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Service for generating embeddings using Qwen2-based models."""
    
    def __init__(
        self, 
        model_name: str = "Alibaba-NLP/gte-Qwen2-7B-instruct",
        device: Optional[str] = None,
        batch_size: int = 32
    ):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name or path of the embedding model
            device: Device to run model on (auto-detected if None)
            batch_size: Batch size for processing multiple texts
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.batch_size = batch_size
        
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.logger.info(f"Using device: {self.device}")
        
        # Initialize model and tokenizer
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model and tokenizer."""
        try:
            self.logger.info(f"Loading embedding model: {self.model_name}")
            
            # Try to load as SentenceTransformer first (easier to use)
            try:
                self.model = SentenceTransformer(self.model_name, device=self.device)
                self.use_sentence_transformer = True
                self.logger.info("Successfully loaded model using SentenceTransformers")
                
            except Exception as e:
                self.logger.warning(f"Failed to load as SentenceTransformer: {e}")
                self.logger.info("Loading as transformers model...")
                
                # Fallback to transformers
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
                self.model = AutoModel.from_pretrained(
                    self.model_name, 
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map=self.device,
                    trust_remote_code=True
                )
                self.use_sentence_transformer = False
                self.logger.info("Successfully loaded model using transformers")
                
        except Exception as e:
            self.logger.error(f"Failed to load embedding model: {str(e)}")
            raise RuntimeError(f"Could not load embedding model: {str(e)}")
    
    def encode(self, texts: Union[str, List[str]], normalize: bool = True) -> np.ndarray:
        """
        Generate embeddings for input texts.
        
        Args:
            texts: Single text string or list of text strings
            normalize: Whether to normalize embeddings to unit vectors
            
        Returns:
            NumPy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            if self.use_sentence_transformer:
                embeddings = self._encode_with_sentence_transformer(texts, normalize)
            else:
                embeddings = self._encode_with_transformers(texts, normalize)
                
            self.logger.debug(f"Generated embeddings for {len(texts)} texts, shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def _encode_with_sentence_transformer(self, texts: List[str], normalize: bool) -> np.ndarray:
        """Encode texts using SentenceTransformer."""
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=normalize,
            show_progress_bar=len(texts) > 10
        )
        return embeddings
    
    def _encode_with_transformers(self, texts: List[str], normalize: bool) -> np.ndarray:
        """Encode texts using transformers model."""
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_embeddings = self._encode_batch(batch_texts)
            all_embeddings.append(batch_embeddings)
        
        embeddings = np.vstack(all_embeddings)
        
        if normalize:
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        return embeddings
    
    def _encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode a single batch of texts."""
        # Tokenize
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=512
        ).to(self.device)
        
        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            
            # Use mean pooling of last hidden states
            embeddings = self._mean_pooling(outputs, inputs['attention_mask'])
            
        return embeddings.cpu().numpy()
    
    def _mean_pooling(self, model_output, attention_mask):
        """Apply mean pooling to get sentence embeddings."""
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        if self.use_sentence_transformer:
            return self.model.get_sentence_embedding_dimension()
        else:
            # Generate a dummy embedding to get dimension
            dummy_embedding = self.encode("test", normalize=False)
            return dummy_embedding.shape[1]
    
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
        
        # Normalize embeddings
        embedding1_norm = embedding1 / np.linalg.norm(embedding1, axis=1, keepdims=True)
        embedding2_norm = embedding2 / np.linalg.norm(embedding2, axis=1, keepdims=True)
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1_norm, embedding2_norm.T)
        return float(similarity[0][0])


class EmbeddingCache:
    """Simple in-memory cache for embeddings."""
    
    def __init__(self, max_size: int = 10000):
        """Initialize cache with maximum size."""
        self.cache = {}
        self.max_size = max_size
        self.access_order = []
    
    def get(self, text: str) -> Optional[np.ndarray]:
        """Get embedding from cache."""
        if text in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(text)
            self.access_order.append(text)
            return self.cache[text]
        return None
    
    def put(self, text: str, embedding: np.ndarray):
        """Store embedding in cache."""
        if len(self.cache) >= self.max_size:
            # Remove least recently used
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
        
        self.cache[text] = embedding
        self.access_order.append(text)
    
    def clear(self):
        """Clear the cache."""
        self.cache.clear()
        self.access_order.clear()


# Factory function for easy initialization
def create_embedding_service(model_name: Optional[str] = None, device: Optional[str] = None) -> EmbeddingService:
    """
    Factory function to create embedding service.
    
    Args:
        model_name: Model name (uses env variable if None)
        device: Device to use (auto-detected if None)
        
    Returns:
        Configured EmbeddingService instance
    """
    if model_name is None:
        model_name = os.getenv("EMBEDDING_MODEL_NAME", "Alibaba-NLP/gte-Qwen2-7B-instruct")
    
    return EmbeddingService(model_name=model_name, device=device)
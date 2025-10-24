"""
Text chunking utilities for splitting documents into manageable pieces.
"""

import os
from typing import List, Dict, Any, Optional


class TextChunker:
    """Text chunking utility with configurable parameters."""
    
    def __init__(self, chunk_size: Optional[int] = None, overlap: Optional[int] = None):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Size of each chunk (uses env variable if None)
            overlap: Overlap between chunks (uses env variable if None)
        """
        self.chunk_size = chunk_size if chunk_size is not None else int(os.getenv("CHUNK_SIZE", "1000"))
        self.overlap = overlap if overlap is not None else int(os.getenv("CHUNK_OVERLAP", "200"))
    
    def chunk_text(self, text: str, chunk_size: Optional[int] = None, overlap: Optional[int] = None, 
                   pages_content: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk (overrides instance default if provided)
            overlap: Overlap between chunks (overrides instance default if provided)
            pages_content: Optional list of page content to track page numbers
            
        Returns:
            List of text chunks with metadata
        """
        if not text:
            return []
        
        # Use provided parameters or instance defaults
        effective_chunk_size = chunk_size if chunk_size is not None else self.chunk_size
        effective_overlap = overlap if overlap is not None else self.overlap
        
        chunks = []
        words = text.split()
        
        # Create page position mapping if pages_content is provided
        page_mapping = {}
        if pages_content:
            current_pos = 0
            for page_info in pages_content:
                page_words = page_info["content"].split()
                for i in range(len(page_words)):
                    page_mapping[current_pos + i] = page_info["page_number"]
                current_pos += len(page_words)
        
        for i in range(0, len(words), effective_chunk_size - effective_overlap):
            chunk_words = words[i:i + effective_chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            # Determine page number for this chunk
            page_number = None
            if page_mapping:
                # Get the page number of the first word in the chunk
                page_number = page_mapping.get(i)
                # If not found, try to find the closest page
                if page_number is None:
                    for word_pos in range(i, min(i + effective_chunk_size, len(words))):
                        if word_pos in page_mapping:
                            page_number = page_mapping[word_pos]
                            break
            
            chunk_data = {
                "text": chunk_text,
                "chunk_id": len(chunks),
                "start_word": i,
                "end_word": min(i + effective_chunk_size, len(words)),
                "chunk_size": len(chunk_words),
                "overlap_size": effective_overlap if i > 0 else 0
            }
            
            # Add page number if available
            if page_number:
                chunk_data["page_number"] = page_number
            
            chunks.append(chunk_data)
        
        return chunks
    
    def chunk_by_sentences(self, text: str, max_sentences: int = 5, overlap_sentences: int = 1) -> List[Dict[str, Any]]:
        """
        Split text into chunks by sentences.
        
        Args:
            text: Text to chunk
            max_sentences: Maximum sentences per chunk
            overlap_sentences: Number of overlapping sentences between chunks
            
        Returns:
            List of text chunks with metadata
        """
        if not text:
            return []
        
        # Simple sentence splitting (can be improved with NLTK or spaCy)
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        chunks = []
        for i in range(0, len(sentences), max_sentences - overlap_sentences):
            chunk_sentences = sentences[i:i + max_sentences]
            chunk_text = '. '.join(chunk_sentences) + '.'
            
            chunks.append({
                "text": chunk_text,
                "chunk_id": len(chunks),
                "start_sentence": i,
                "end_sentence": min(i + max_sentences, len(sentences)),
                "sentence_count": len(chunk_sentences),
                "overlap_sentences": overlap_sentences if i > 0 else 0
            })
        
        return chunks
    
    def chunk_by_paragraphs(self, text: str, max_paragraphs: int = 3, overlap_paragraphs: int = 1) -> List[Dict[str, Any]]:
        """
        Split text into chunks by paragraphs.
        
        Args:
            text: Text to chunk
            max_paragraphs: Maximum paragraphs per chunk
            overlap_paragraphs: Number of overlapping paragraphs between chunks
            
        Returns:
            List of text chunks with metadata
        """
        if not text:
            return []
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        for i in range(0, len(paragraphs), max_paragraphs - overlap_paragraphs):
            chunk_paragraphs = paragraphs[i:i + max_paragraphs]
            chunk_text = '\n\n'.join(chunk_paragraphs)
            
            chunks.append({
                "text": chunk_text,
                "chunk_id": len(chunks),
                "start_paragraph": i,
                "end_paragraph": min(i + max_paragraphs, len(paragraphs)),
                "paragraph_count": len(chunk_paragraphs),
                "overlap_paragraphs": overlap_paragraphs if i > 0 else 0
            })
        
        return chunks


def create_text_chunker(chunk_size: Optional[int] = None, overlap: Optional[int] = None) -> TextChunker:
    """
    Factory function to create a text chunker.
    
    Args:
        chunk_size: Size of each chunk (uses env variable if None)
        overlap: Overlap between chunks (uses env variable if None)
        
    Returns:
        Configured TextChunker instance
    """
    return TextChunker(chunk_size=chunk_size, overlap=overlap)


def chunk_text(text: str, chunk_size: Optional[int] = None, overlap: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to chunk text without creating a chunker instance.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk (uses env variable if None)
        overlap: Overlap between chunks (uses env variable if None)
        
    Returns:
        List of text chunks with metadata
    """
    chunker = create_text_chunker(chunk_size=chunk_size, overlap=overlap)
    return chunker.chunk_text(text)
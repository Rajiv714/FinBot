def chunk_text(self, text: str, chunk_size: Optional[int] = None, overlap: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk (uses env variable if None)
            overlap: Overlap between chunks (uses env variable if None)
            
        Returns:
            List of text chunks with metadata
        """
        if not text:
            return []
        
        # Use environment variables if not provided
        if chunk_size is None:
            chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        if overlap is None:
            overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                "text": chunk_text,
                "chunk_id": len(chunks),
                "start_word": i,
                "end_word": min(i + chunk_size, len(words)),
                "chunk_size": len(chunk_words),
                "overlap_size": overlap if i > 0 else 0
            })
        
        return chunks
"""
Document ingestion service - Business logic for PDF processing and indexing
"""
import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src directory to path
src_path = str(Path(__file__).parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from utils.parsing import DocumentParser
from utils.chunking import create_text_chunker
from vectorstore.qdrant_client import create_qdrant_client
from embeddings.embeddings import create_embedding_service


class IngestionService:
    """Service for document ingestion and indexing"""
    
    def __init__(self):
        """Initialize ingestion service"""
        self.document_parser = DocumentParser()
        self.text_chunker = create_text_chunker()
        self.embedding_service = create_embedding_service()
        embedding_dim = self.embedding_service.get_embedding_dimension()
        self.vector_client = create_qdrant_client(vector_size=embedding_dim)
    
    def ingest_documents(
        self,
        data_folder: str = "Data",
        clear_existing: bool = False,
        file_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ingest PDF documents into the vector store.
        
        Args:
            data_folder: Folder containing PDF files
            clear_existing: Whether to clear existing collection
            file_paths: Specific files to ingest (overrides data_folder)
            
        Returns:
            Dictionary with ingestion results
        """
        start_time = time.time()
        errors = []
        
        try:
            print("Starting document ingestion...")
            
            # Get PDF files to process
            if file_paths:
                pdf_files = [Path(fp) for fp in file_paths if Path(fp).suffix.lower() == '.pdf']
            else:
                data_path = Path(data_folder)
                if not data_path.exists():
                    return {
                        "success": False,
                        "files_processed": 0,
                        "total_chunks": 0,
                        "execution_time": time.time() - start_time,
                        "errors": [f"Data folder not found: {data_folder}"]
                    }
                pdf_files = list(data_path.glob("*.pdf"))
            
            if not pdf_files:
                return {
                    "success": False,
                    "files_processed": 0,
                    "total_chunks": 0,
                    "execution_time": time.time() - start_time,
                    "errors": ["No PDF files found"]
                }
            
            print(f"Found {len(pdf_files)} PDF files to process")
            
            if clear_existing:
                print("Clearing existing knowledge base...")
                # Vector store will handle collection recreation
            
            # Process all PDFs
            all_documents = []
            total_files_processed = 0
            
            for i, pdf_path in enumerate(pdf_files, 1):
                print(f"Processing [{i}/{len(pdf_files)}]: {pdf_path.name}")
                
                try:
                    parsed_doc = self.document_parser.parse_document(str(pdf_path))
                    
                    if parsed_doc["success"]:
                        # Create document object for chunking
                        class Document:
                            def __init__(self, content, metadata):
                                self.page_content = content
                                self.metadata = metadata
                        
                        all_documents.append(Document(
                            parsed_doc["content"],
                            parsed_doc["metadata"]
                        ))
                        total_files_processed += 1
                        print(f"   ✓ Successfully processed {pdf_path.name}")
                    else:
                        error_msg = f"No content extracted from {pdf_path.name}"
                        errors.append(error_msg)
                        print(f"   ⚠ {error_msg}")
                        
                except Exception as e:
                    error_msg = f"Error processing {pdf_path.name}: {str(e)}"
                    errors.append(error_msg)
                    print(f"   ✗ {error_msg}")
            
            # Create chunks and index
            if all_documents:
                print(f"\nCreating chunks from {len(all_documents)} documents...")
                
                chunks = []
                for doc in all_documents:
                    pages_content = doc.metadata.get("pages_content", [])
                    doc_chunks = self.text_chunker.chunk_text(
                        doc.page_content,
                        pages_content=pages_content
                    )
                    
                    for chunk in doc_chunks:
                        class ChunkDoc:
                            def __init__(self, text, metadata):
                                self.page_content = text
                                self.metadata = metadata
                        
                        chunks.append(ChunkDoc(
                            chunk["text"],
                            {**doc.metadata, **chunk}
                        ))
                
                print(f"Created {len(chunks)} chunks")
                
                # Generate embeddings and store
                print("Creating embeddings and storing in vector database...")
                texts = [chunk.page_content for chunk in chunks]
                metadatas = [chunk.metadata for chunk in chunks]
                embeddings = self.embedding_service.encode(texts)
                
                self.vector_client.add_documents(texts, embeddings, metadatas)
                
                total_time = time.time() - start_time
                
                print(f"\n{'='*60}")
                print(f"✓ INGESTION COMPLETED")
                print(f"{'='*60}")
                print(f"Files processed: {total_files_processed}/{len(pdf_files)}")
                print(f"Total chunks: {len(chunks)}")
                print(f"Execution time: {total_time:.2f}s")
                if errors:
                    print(f"Errors: {len(errors)}")
                print(f"{'='*60}")
                
                return {
                    "success": True,
                    "files_processed": total_files_processed,
                    "total_chunks": len(chunks),
                    "execution_time": total_time,
                    "errors": errors
                }
            else:
                return {
                    "success": False,
                    "files_processed": 0,
                    "total_chunks": 0,
                    "execution_time": time.time() - start_time,
                    "errors": errors + ["No documents to index"]
                }
                
        except Exception as e:
            return {
                "success": False,
                "files_processed": 0,
                "total_chunks": 0,
                "execution_time": time.time() - start_time,
                "errors": errors + [f"Ingestion failed: {str(e)}"]
            }


# Global service instance
_ingestion_service = None


def get_ingestion_service() -> IngestionService:
    """Get or create ingestion service singleton"""
    global _ingestion_service
    if _ingestion_service is None:
        _ingestion_service = IngestionService()
    return _ingestion_service

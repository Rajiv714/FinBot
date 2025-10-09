#!/usr/bin/env python3
"""
Simple data ingestion pipeline for FinBot.
Process PDF documents from the Data/ folder and store them in the vector database.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src directory to path
current_dir = Path(__file__).parent.parent  # Go up to src directory
sys.path.insert(0, str(current_dir))

from utils.parsing import DocumentParser
from utils.chunking import create_text_chunker
from embeddings.embeddings import create_embedding_service
from vectorstore.qdrant_client import create_qdrant_client


class DataIngestionPipeline:
    """Simple pipeline for ingesting financial documents into the vector database."""
    
    def __init__(self, data_folder: str = "Data"):
        """
        Initialize the data ingestion pipeline.
        
        Args:
            data_folder: Path to folder containing PDF documents
        """
        self.data_folder = Path(data_folder)
        self.document_parser = DocumentParser()
        self.text_chunker = create_text_chunker()
        self.embedding_service = create_embedding_service()
        
        # Load default chunking parameters
        self.default_chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.default_chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        
        # Get embedding dimension and create vector DB
        embedding_dim = self.embedding_service.get_embedding_dimension()
        self.vector_db = create_qdrant_client(vector_size=embedding_dim)
    
    def _get_chunking_params(self, chunk_size: Optional[int], chunk_overlap: Optional[int]) -> tuple:
        """Get chunking parameters with fallback to defaults."""
        effective_chunk_size = chunk_size if chunk_size is not None else self.default_chunk_size
        effective_chunk_overlap = chunk_overlap if chunk_overlap is not None else self.default_chunk_overlap
        return effective_chunk_size, effective_chunk_overlap
    
    def ingest_documents(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        clear_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Ingest all PDF documents from the data folder.
        
        Args:
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between consecutive chunks
            clear_existing: Whether to clear existing documents first
            
        Returns:
            Summary of ingestion results
        """
        effective_chunk_size, effective_chunk_overlap = self._get_chunking_params(chunk_size, chunk_overlap)
        
        if not self.data_folder.exists():
            return {"status": "error", "message": f"Data folder does not exist: {self.data_folder}"}
        
        try:
            # Clear existing documents if requested
            if clear_existing:
                self.vector_db.clear_collection()
            
            # Parse all PDF documents
            parsed_documents = self.document_parser.parse_documents_batch(str(self.data_folder))
            
            if not parsed_documents:
                return {
                    "status": "warning",
                    "message": "No documents found or successfully parsed",
                    "documents_processed": 0
                }
            
            # Process documents
            total_chunks = 0
            for doc in parsed_documents:
                # Chunk the document with configurable parameters
                chunks = self.text_chunker.chunk_text(
                    doc["content"], 
                    chunk_size=effective_chunk_size, 
                    overlap=effective_chunk_overlap
                )
                
                if not chunks:
                    continue
                
                # Prepare data for embedding
                texts = [chunk["text"] for chunk in chunks]
                metadatas = []
                
                for chunk in chunks:
                    metadata = doc["metadata"].copy()
                    metadata.update(chunk)
                    metadatas.append(metadata)
                
                # Generate embeddings
                embeddings = self.embedding_service.encode(texts)
                
                # Store in vector database
                self.vector_db.add_documents(texts, embeddings, metadatas)
                total_chunks += len(chunks)
            
            return {
                "status": "success",
                "message": "Documents ingested successfully",
                "documents_processed": len(parsed_documents),
                "chunks_created": total_chunks,
                "data_folder": str(self.data_folder),
                "chunk_size": effective_chunk_size,
                "chunk_overlap": effective_chunk_overlap
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error during document ingestion: {str(e)}",
                "documents_processed": 0
            }
    
    def ingest_single_file(
        self,
        file_path: str,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Ingest a single PDF file.
        
        Args:
            file_path: Path to the PDF file
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Ingestion results
        """
        effective_chunk_size, effective_chunk_overlap = self._get_chunking_params(chunk_size, chunk_overlap)
        
        try:
            # Parse the document
            parsed_doc = self.document_parser.parse_document(file_path)
            
            if not parsed_doc["success"]:
                return {
                    "status": "error",
                    "message": f"Failed to parse document: {parsed_doc['metadata'].get('error', 'Unknown error')}",
                    "file_path": file_path
                }
            
            # Chunk the document with configurable parameters
            chunks = self.text_chunker.chunk_text(
                parsed_doc["content"], 
                chunk_size=effective_chunk_size, 
                overlap=effective_chunk_overlap
            )
            
            if not chunks:
                return {
                    "status": "error",
                    "message": "No chunks created from document",
                    "file_path": file_path
                }
            
            # Prepare data for embedding
            texts = [chunk["text"] for chunk in chunks]
            metadatas = []
            
            for chunk in chunks:
                metadata = parsed_doc["metadata"].copy()
                metadata.update(chunk)
                metadatas.append(metadata)
            
            # Generate embeddings
            embeddings = self.embedding_service.encode(texts)
            
            # Store in vector database
            self.vector_db.add_documents(texts, embeddings, metadatas)
            
            return {
                "status": "success",
                "message": "File ingested successfully",
                "file_path": file_path,
                "chunks_created": len(chunks),
                "chunk_size": effective_chunk_size,
                "chunk_overlap": effective_chunk_overlap
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error ingesting file {file_path}: {str(e)}",
                "file_path": file_path
            }
    
    def list_data_files(self) -> List[str]:
        """List all PDF files in the data folder."""
        if not self.data_folder.exists():
            return []
        
        pdf_files = []
        for file_path in self.data_folder.rglob("*.pdf"):
            pdf_files.append(str(file_path))
        
        return pdf_files
    
    def get_collection_status(self) -> Dict[str, Any]:
        """Get status of the vector database collection."""
        try:
            return self.vector_db.get_collection_info()
        except Exception as e:
            return {"error": str(e)}


def main():
    """Main entry point for data ingestion script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="FinBot Data Ingestion Pipeline")
    
    parser.add_argument(
        "--data-folder",
        default="Data",
        help="Path to data folder containing PDF documents (default: Data)"
    )
    
    parser.add_argument(
        "--ingest-all",
        action="store_true",
        help="Ingest all PDF documents from the data folder"
    )
    
    parser.add_argument(
        "--file",
        help="Ingest a single PDF file"
    )
    
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing documents before ingestion"
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Size of text chunks (default: 1000)"
    )
    
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between chunks (default: 200)"
    )
    
    parser.add_argument(
        "--list-files",
        action="store_true",
        help="List all PDF files in the data folder"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show vector database collection status"
    )
    
    args = parser.parse_args()
    
    # Initialize pipeline
    try:
        pipeline = DataIngestionPipeline(data_folder=args.data_folder)
    except Exception as e:
        print(f"Failed to initialize pipeline: {str(e)}")
        return 1
    
    # Execute requested action
    try:
        if args.list_files:
            print(f"\nPDF files in {args.data_folder}:")
            files = pipeline.list_data_files()
            if files:
                for i, file_path in enumerate(files, 1):
                    print(f"  {i}. {file_path}")
                print(f"\nTotal: {len(files)} files")
            else:
                print("  No PDF files found")
        
        elif args.status:
            print("\nVector Database Status:")
            status = pipeline.get_collection_status()
            if "error" in status:
                print(f"  Error: {status['error']}")
            else:
                print(f"  Collection: {status.get('name', 'Unknown')}")
                print(f"  Documents: {status.get('points_count', 0)}")
                print(f"  Vector Size: {status.get('vector_size', 'Unknown')}")
                print(f"  Status: {status.get('status', 'Unknown')}")
        
        elif args.file:
            print(f"\nIngesting single file: {args.file}")
            result = pipeline.ingest_single_file(
                file_path=args.file,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap
            )
            
            if result["status"] == "success":
                print(f"  Success! Chunks created: {result['chunks_created']}")
            else:
                print(f"  Failed: {result['message']}")
        
        elif args.ingest_all:
            print(f"\nIngesting all documents from: {args.data_folder}")
            if args.clear:
                print("  Clearing existing documents...")
            
            result = pipeline.ingest_documents(
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap,
                clear_existing=args.clear
            )
            
            if result["status"] == "success":
                print(f"  Success!")
                print(f"  PDF files processed: {result['documents_processed']}")
                print(f"  Chunks created: {result['chunks_created']}")
            else:
                print(f"  Failed: {result['message']}")
        
        else:
            parser.print_help()
            return 0
        
        return 0
        
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
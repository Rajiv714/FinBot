#!/usr/bin/env python3
"""
Data ingestion pipeline for FinBot.
Process PDF documents from the Data/ folder and store them in the vector database.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import argparse
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from document_parser import DocumentParser
from rag_pipeline import create_rag_pipeline

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataIngestionPipeline:
    """Pipeline for ingesting financial documents into the vector database."""
    
    def __init__(self, data_folder: str = "Data"):
        """
        Initialize the data ingestion pipeline.
        
        Args:
            data_folder: Path to folder containing PDF documents
        """
        self.data_folder = Path(data_folder)
        self.document_parser = DocumentParser()
        
        # Initialize RAG pipeline (which includes vector DB and embedding service)
        self.rag_pipeline = create_rag_pipeline()
        
        logger.info(f"Data ingestion pipeline initialized for folder: {self.data_folder}")
    
    def ingest_documents(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
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
        if not self.data_folder.exists():
            error_msg = f"Data folder does not exist: {self.data_folder}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        try:
            # Clear existing documents if requested
            if clear_existing:
                logger.info("Clearing existing documents from vector database...")
                self.rag_pipeline.vector_db.clear_collection()
            
            # Parse all PDF documents
            logger.info("Parsing PDF documents...")
            parsed_documents = self.document_parser.parse_documents_batch(str(self.data_folder))
            
            if not parsed_documents:
                return {
                    "status": "warning",
                    "message": "No documents found or successfully parsed",
                    "documents_processed": 0
                }
            
            logger.info(f"Successfully parsed {len(parsed_documents)} documents")
            
            # Add documents to RAG pipeline (this will chunk, embed, and store them)
            ingestion_result = self.rag_pipeline.add_documents(
                documents=parsed_documents,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            # Add summary information
            ingestion_result.update({
                "data_folder": str(self.data_folder),
                "pdf_files_found": len(parsed_documents),
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "cleared_existing": clear_existing
            })
            
            return ingestion_result
            
        except Exception as e:
            error_msg = f"Error during document ingestion: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "documents_processed": 0
            }
    
    def ingest_single_file(
        self,
        file_path: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
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
        try:
            logger.info(f"Ingesting single file: {file_path}")
            
            # Parse the document
            parsed_doc = self.document_parser.parse_document(file_path)
            
            if not parsed_doc["success"]:
                return {
                    "status": "error",
                    "message": f"Failed to parse document: {parsed_doc['metadata'].get('error', 'Unknown error')}",
                    "file_path": file_path
                }
            
            # Add to RAG pipeline
            ingestion_result = self.rag_pipeline.add_documents(
                documents=[parsed_doc],
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            ingestion_result.update({
                "file_path": file_path,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap
            })
            
            return ingestion_result
            
        except Exception as e:
            error_msg = f"Error ingesting file {file_path}: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
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
            return self.rag_pipeline.vector_db.get_collection_info()
        except Exception as e:
            return {"error": str(e)}


def main():
    """Main entry point for data ingestion script."""
    parser = argparse.ArgumentParser(
        description="FinBot Data Ingestion Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest all documents from Data/ folder
  python ingest_data.py --ingest-all
  
  # Clear existing data and ingest all documents
  python ingest_data.py --ingest-all --clear
  
  # Ingest a single file
  python ingest_data.py --file Data/document.pdf
  
  # List all PDF files in data folder
  python ingest_data.py --list-files
  
  # Check collection status
  python ingest_data.py --status
        """
    )
    
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
        logger.error(f"Failed to initialize pipeline: {str(e)}")
        return 1
    
    # Execute requested action
    try:
        if args.list_files:
            print(f"\n📁 PDF files in {args.data_folder}:")
            files = pipeline.list_data_files()
            if files:
                for i, file_path in enumerate(files, 1):
                    print(f"  {i}. {file_path}")
                print(f"\nTotal: {len(files)} files")
            else:
                print("  No PDF files found")
        
        elif args.status:
            print("\n📊 Vector Database Status:")
            status = pipeline.get_collection_status()
            if "error" in status:
                print(f"  ❌ Error: {status['error']}")
            else:
                print(f"  Collection: {status.get('name', 'Unknown')}")
                print(f"  Documents: {status.get('points_count', 0)}")
                print(f"  Vector Size: {status.get('vector_size', 'Unknown')}")
                print(f"  Status: {status.get('status', 'Unknown')}")
        
        elif args.file:
            print(f"\n📄 Ingesting single file: {args.file}")
            result = pipeline.ingest_single_file(
                file_path=args.file,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap
            )
            
            if result["status"] == "success":
                print(f"  ✅ Success!")
                print(f"  Chunks created: {result['chunks_created']}")
                print(f"  Embeddings generated: {result['embeddings_generated']}")
            else:
                print(f"  ❌ Failed: {result['message']}")
        
        elif args.ingest_all:
            print(f"\n📚 Ingesting all documents from: {args.data_folder}")
            if args.clear:
                print("  🗑️  Clearing existing documents...")
            
            result = pipeline.ingest_documents(
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap,
                clear_existing=args.clear
            )
            
            if result["status"] == "success":
                print(f"  ✅ Success!")
                print(f"  PDF files processed: {result['pdf_files_found']}")
                print(f"  Chunks created: {result['chunks_created']}")
                print(f"  Embeddings generated: {result['embeddings_generated']}")
            else:
                print(f"  ❌ Failed: {result['message']}")
        
        else:
            parser.print_help()
            return 0
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
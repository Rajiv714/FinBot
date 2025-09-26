"""
Document parser for financial documents using Docling.
Handles PDF files with text and images.
"""

import os
from typing import List, Dict, Any
from pathlib import Path
import logging
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import ConversionResult
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend


class DocumentParser:
    """Parser for financial documents using Docling."""
    
    def __init__(self):
        """Initialize the document parser."""
        self.logger = logging.getLogger(__name__)
        
        # Configure pipeline options for better PDF processing
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = 2.0
        pipeline_options.generate_page_images = True
        pipeline_options.generate_table_images = True
        
        # Initialize converter with optimized settings
        self.converter = DocumentConverter(
            pdf_backend=PyPdfiumDocumentBackend,
            pipeline_options=pipeline_options
        )
    
    def parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a single document and extract text content.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing parsed content and metadata
        """
        try:
            self.logger.info(f"Parsing document: {file_path}")
            
            # Convert document
            result: ConversionResult = self.converter.convert(file_path)
            
            # Extract text content
            text_content = result.document.export_to_markdown()
            
            # Get document metadata
            metadata = {
                "source": file_path,
                "filename": Path(file_path).name,
                "pages": len(result.document.pages) if hasattr(result.document, 'pages') else 1,
                "title": self._extract_title(text_content),
                "document_type": "financial_document"
            }
            
            return {
                "content": text_content,
                "metadata": metadata,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing document {file_path}: {str(e)}")
            return {
                "content": "",
                "metadata": {"source": file_path, "error": str(e)},
                "success": False
            }
    
    def parse_documents_batch(self, folder_path: str) -> List[Dict[str, Any]]:
        """
        Parse all PDF documents in a folder.
        
        Args:
            folder_path: Path to folder containing PDF files
            
        Returns:
            List of parsed document dictionaries
        """
        parsed_docs = []
        pdf_files = self._get_pdf_files(folder_path)
        
        self.logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            parsed_doc = self.parse_document(pdf_file)
            if parsed_doc["success"]:
                parsed_docs.append(parsed_doc)
            else:
                self.logger.warning(f"Failed to parse: {pdf_file}")
        
        return parsed_docs
    
    def _get_pdf_files(self, folder_path: str) -> List[str]:
        """Get all PDF files in a folder."""
        folder = Path(folder_path)
        if not folder.exists():
            self.logger.error(f"Folder does not exist: {folder_path}")
            return []
        
        pdf_files = []
        for file_path in folder.rglob("*.pdf"):
            pdf_files.append(str(file_path))
        
        return pdf_files
    
    def _extract_title(self, content: str) -> str:
        """Extract title from document content."""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 5 and len(line) < 100:
                # Simple heuristic for title detection
                if not line.startswith('#') and not line.startswith('-'):
                    return line
        return "Untitled Document"
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks with metadata
        """
        if not text:
            return []
        
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                "text": chunk_text,
                "chunk_id": len(chunks),
                "start_word": i,
                "end_word": min(i + chunk_size, len(words))
            })
        
        return chunks


# Alternative parser using PyMuPDF (if preferred)
try:
    import fitz  # PyMuPDF
    
    class PyMuPDFParser:
        """Alternative PDF parser using PyMuPDF."""
        
        def __init__(self):
            self.logger = logging.getLogger(__name__)
        
        def parse_document(self, file_path: str) -> Dict[str, Any]:
            """Parse document using PyMuPDF."""
            try:
                doc = fitz.open(file_path)
                text_content = ""
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text_content += page.get_text()
                
                doc.close()
                
                metadata = {
                    "source": file_path,
                    "filename": Path(file_path).name,
                    "pages": len(doc),
                    "document_type": "financial_document"
                }
                
                return {
                    "content": text_content,
                    "metadata": metadata,
                    "success": True
                }
                
            except Exception as e:
                self.logger.error(f"Error parsing with PyMuPDF: {str(e)}")
                return {
                    "content": "",
                    "metadata": {"source": file_path, "error": str(e)},
                    "success": False
                }

except ImportError:
    PyMuPDFParser = None
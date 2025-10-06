"""
Simple document parser for PDF files.
"""

import os
from typing import List, Dict, Any
from pathlib import Path

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from docling.document_converter import DocumentConverter
    HAS_DOCLING = True
except ImportError:
    HAS_DOCLING = False


class DocumentParser:
    """Simple PDF parser."""
    
    def __init__(self):
        """Initialize the document parser."""
        if HAS_PYMUPDF:
            self.use_pymupdf = True
        elif HAS_DOCLING:
            self.use_pymupdf = False
            self.converter = DocumentConverter()
        else:
            raise ImportError("Either PyMuPDF or Docling is required for PDF parsing")
    
    def parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a single PDF document.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing parsed content and metadata
        """
        try:
            if self.use_pymupdf:
                return self._parse_with_pymupdf(file_path)
            else:
                return self._parse_with_docling(file_path)
        except Exception as e:
            return {
                "content": "",
                "metadata": {"source": file_path, "error": str(e)},
                "success": False
            }
    
    def _parse_with_pymupdf(self, file_path: str) -> Dict[str, Any]:
        """Parse using PyMuPDF."""
        doc = fitz.open(file_path)
        text_content = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content += page.get_text() + "\n"
        
        doc.close()
        
        metadata = {
            "source": file_path,
            "filename": Path(file_path).name,
            "pages": len(doc),
            "title": self._extract_title(text_content),
            "document_type": "financial_document"
        }
        
        return {
            "content": text_content,
            "metadata": metadata,
            "success": True
        }
    
    def _parse_with_docling(self, file_path: str) -> Dict[str, Any]:
        """Parse using Docling."""
        result = self.converter.convert(file_path)
        text_content = result.document.export_to_markdown()
        
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
        
        for pdf_file in pdf_files:
            parsed_doc = self.parse_document(pdf_file)
            if parsed_doc["success"]:
                parsed_docs.append(parsed_doc)
        
        return parsed_docs
    
    def _get_pdf_files(self, folder_path: str) -> List[str]:
        """Get all PDF files in a folder."""
        folder = Path(folder_path)
        if not folder.exists():
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


class PyMuPDFParser:
    """Simple PDF parser using PyMuPDF."""
    
    def __init__(self):
        if not HAS_PYMUPDF:
            raise ImportError("PyMuPDF is required for this parser")
    
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
            return {
                "content": "",
                "metadata": {"source": file_path, "error": str(e)},
                "success": False
            }
"""
Simple document parser for PDF files using Docling with OCR.
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.backend.pdf_backend import PdfFormatOption
    HAS_DOCLING = True
except ImportError:
    HAS_DOCLING = False


class DocumentParser:
    """PDF parser using Docling with OCR capabilities."""
    
    def __init__(self):
        """Initialize the document parser with OCR-enabled Docling."""
        if not HAS_DOCLING:
            raise ImportError("Docling is required for PDF parsing")
        
        # Configure pipeline options for OCR and table structure
        options = PdfPipelineOptions()
        options.do_ocr = options.do_table_structure = True
        options.table_structure_options.do_cell_matching = True
        
        self.converter = DocumentConverter({
            InputFormat.PDF: PdfFormatOption(pipeline_options=options)
        })
    
    def parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a single PDF document using Docling with OCR.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing parsed content and metadata
        """
        try:
            return self._parse_with_docling(file_path)
        except Exception as e:
            return {
                "content": "",
                "metadata": {"source": file_path, "error": str(e)},
                "success": False
            }
    
    def _parse_with_docling(self, file_path: str) -> Dict[str, Any]:
        """Parse using Docling with OCR capabilities."""
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
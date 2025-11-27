import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
 

class DocumentParser:
    def __init__(self):
        # Configure pipeline options for OCR and table structure
        options = PdfPipelineOptions()
        options.do_ocr = options.do_table_structure = True
        options.table_structure_options.do_cell_matching = True
        
        self.converter = DocumentConverter({
            InputFormat.PDF: PdfFormatOption(pipeline_options=options)
        })
    
    def parse_document(self, file_path: str) -> Dict[str, Any]:
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
        
        # CLEAN the text content to remove junk
        text_content = self._clean_text(text_content)
        
        # Extract page-wise content for better tracking
        pages_content = []
        if hasattr(result.document, 'pages'):
            for page_num, page in enumerate(result.document.pages, 1):
                page_text = page.export_to_markdown() if hasattr(page, 'export_to_markdown') else ""
                # CLEAN page text too
                page_text = self._clean_text(page_text)
                pages_content.append({
                    "page_number": page_num,
                    "content": page_text
                })
        
        metadata = {
            "source": file_path,
            "filename": Path(file_path).name,
            "pages": len(result.document.pages) if hasattr(result.document, 'pages') else 1,
            "title": self._extract_title(text_content),
            "document_type": "financial_document",
            "pages_content": pages_content  # Add page-wise content
        }
        
        return {
            "content": text_content,
            "metadata": metadata,
            "success": True
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text by removing junk and normalizing."""
        if not text:
            return text
        
        # Remove excessive whitespace and normalize line breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 2 consecutive newlines
        
        # Remove page numbers (standalone numbers)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Remove common headers/footers patterns
        text = re.sub(r'(?i)(page \d+( of \d+)?)', '', text)
        text = re.sub(r'(?i)(copyright|©|\(c\)).*\d{4}', '', text)
        
        # Remove HTML-like tags that sometimes appear
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove excessive dashes/underscores (decorative lines)
        text = re.sub(r'\n[-_]{3,}\n', '\n', text)
        
        # Remove URLs (usually not useful in financial docs)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Normalize multiple spaces to single space
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove lines with only special characters
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Keep line if it has at least 3 alphanumeric characters
            if re.search(r'[a-zA-Z0-9]{3,}', line):
                cleaned_lines.append(line.strip())
        
        text = '\n'.join(cleaned_lines)
        
        # Final whitespace cleanup
        text = text.strip()
        
        return text
    
    def parse_documents_batch(self, folder_path: str) -> List[Dict[str, Any]]:
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
"""
Document summariser service - Business logic for financial document analysis
"""
import sys
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

# Add src directory to path
src_path = str(Path(__file__).parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from summariser import create_document_summariser


class SummariserService:
    """Service for document summarisation and analysis"""
    
    def __init__(self):
        """Initialize summariser service"""
        self.summariser = create_document_summariser()
    
    def analyze_document(
        self,
        file_content: bytes,
        filename: str,
        user_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a financial document.
        
        Args:
            file_content: Binary content of the uploaded file
            filename: Name of the file
            user_query: Optional user query to answer
            
        Returns:
            Dictionary with analysis results
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        try:
            print(f"Analyzing document: {filename}")
            
            # Process document
            result = self.summariser.process_document(
                file_path=tmp_file_path,
                user_query=user_query.strip() if user_query and user_query.strip() else None
            )
            
            if result.get("success"):
                print(f"✓ Successfully analyzed {filename}")
                print(f"  Document type: {result['document_type']}")
                print(f"  Text length: {result['text_length']} characters")
            else:
                print(f"✗ Failed to analyze {filename}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Service error: {str(e)}"
            }
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)


# Global service instance
_summariser_service = None


def get_summariser_service() -> SummariserService:
    """Get or create summariser service singleton"""
    global _summariser_service
    if _summariser_service is None:
        _summariser_service = SummariserService()
    return _summariser_service

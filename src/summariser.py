"""
Document Summariser - Core logic for financial document analysis
Follows FinBot architecture patterns
"""
import os
import re
import requests
import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class DocumentSummariser:
    """Analyzes financial documents using OCR and LLM."""
    
    DOCUMENT_PATTERNS = {
        "loan_agreement": [
            r"loan agreement", r"interest rate", r"borrower", 
            r"lender", r"repayment", r"principal amount"
        ],
        "personal_loan": [
            r"personal loan", r"unsecured loan"
        ],
        "mortgage": [
            r"mortgage", r"property", r"collateral"
        ],
        "credit_card": [
            r"credit card", r"annual fee", r"apr"
        ],
        "insurance": [
            r"insurance policy", r"premium", r"coverage"
        ],
        "investment": [
            r"mutual fund", r"sip", r"investment"
        ]
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        api_url: Optional[str] = None,
        max_text_length: Optional[int] = None
    ):
        """
        Initialize the summariser with API credentials.
        
        Args:
            api_key: OpenRouter API key (from .env if not provided)
            model: Model identifier (from .env if not provided)
            api_url: API URL (from .env if not provided)
            max_text_length: Max text length (from .env if not provided)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL", "x-ai/grok-4.1-fast:free")
        self.api_url = api_url or os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.max_text_length = max_text_length or int(os.getenv("MAX_TEXT_LENGTH", "15000"))
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    def extract_text(self, file_path: str) -> Optional[str]:
        """
        Extract text from document using PyMuPDF with OCR fallback.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Try direct text extraction first (fast for digital PDFs)
                page_text = page.get_text()
                
                # If text extraction fails or returns very little, use OCR
                if len(page_text.strip()) < 50:
                    # Use PyMuPDF's built-in OCR
                    pix = page.get_pixmap(dpi=300)
                    page_text = page.get_textpage_ocr().extractText()
                
                text += page_text + "\n\n"
            
            doc.close()
            return text if text.strip() else None
            
        except Exception as e:
            print(f"Text extraction error: {str(e)}")
            return None
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw text from OCR
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        # Keep only safe characters
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\₹\%\@\/\n]', '', text)
        # Normalize currency symbols
        text = text.replace('Rs.', '₹').replace('Rs', '₹')
        # Remove page numbers
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def identify_document_type(self, text: str) -> str:
        """
        Identify the type of financial document.
        
        Args:
            text: Cleaned document text
            
        Returns:
            Document type identifier
        """
        text_lower = text.lower()
        scores = {
            doc_type: sum(
                1 for pattern in patterns 
                if re.search(pattern, text_lower, re.IGNORECASE)
            )
            for doc_type, patterns in self.DOCUMENT_PATTERNS.items()
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return "general_financial_document"
        
        return max(scores, key=scores.get)
    
    def create_system_prompt(self, doc_type: str, user_query: Optional[str] = None) -> str:
        """
        Create system prompt for LLM based on document type.
        
        Args:
            doc_type: Type of document identified
            user_query: Optional user query to address
            
        Returns:
            System prompt string
        """
        doc_type_formatted = doc_type.replace('_', ' ').title()
        
        # Extract language instruction if present in user_query
        language_instruction = ""
        cleaned_query = user_query
        if user_query:
            # Check if query starts with language instruction
            if "[Analyze in " in user_query and " language]" in user_query:
                import re
                match = re.search(r'\[Analyze in (.+?) language\]', user_query)
                if match:
                    lang_name = match.group(1)
                    language_instruction = f"IMPORTANT: Provide your ENTIRE response in {lang_name}. All sections (Summary, Important Points, Warnings, Action Points) MUST be in {lang_name}.\n\n"
                    cleaned_query = re.sub(r'\[Analyze in .+? language\]\s*', '', user_query).strip()
        
        base_prompt = f"""{language_instruction}You are a financial advisor helping users understand their financial documents.
The document type is: {doc_type_formatted}

Your task:
1. Provide a SIMPLE summary
2. {'Answer the user query: "' + cleaned_query + '" in simple terms' if cleaned_query else 'Skip to next step'}
3. Identify and explain IMPORTANT POINTS - especially:
   - Hidden charges or penalties
   - High interest rates
   - Confusing terms
   - Any unfair clauses
4. List ACTION POINTS - what the user needs to do
5. WARNINGS - highlight anything that could cause financial harm

Use clear language. Use short sentences. Avoid jargon.
If technical terms are unavoidable, explain them simply.

Format your response clearly with these sections:
- **Summary**
{('- **Answer to Your Question**' if cleaned_query else '')}
- **Important Points**
- **Warnings**
- **Action Points**"""
        
        return base_prompt
    
    def call_llm(self, text: str, system_prompt: str) -> Optional[str]:
        """
        Call LLM API to analyze the document.
        
        Args:
            text: Cleaned document text
            system_prompt: System prompt for the LLM
            
        Returns:
            Analysis result or None if call fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "FinBot-Document-Summariser",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please analyze this financial document:\n\n{text}"}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=data, 
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            print(f"API Error: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
    
    def process_document(
        self, 
        file_path: str, 
        user_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a financial document through the complete pipeline.
        
        Args:
            file_path: Path to the document file
            user_query: Optional user query to answer
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Step 1: Extract text using OCR
            print("Extracting text from document...")
            raw_text = self.extract_text(file_path)
            if not raw_text:
                return {
                    "success": False,
                    "error": "Failed to extract text from document"
                }
            
            # Step 2: Clean the extracted text
            print("Cleaning extracted text...")
            cleaned_text = self.clean_text(raw_text)
            
            if len(cleaned_text) > self.max_text_length:
                cleaned_text = cleaned_text[:self.max_text_length] + "\n\n[Document truncated for analysis]"
            
            # Step 3: Identify document type
            doc_type = self.identify_document_type(cleaned_text)
            doc_type_formatted = doc_type.replace('_', ' ').title()
            
            # Step 4: Analyze with LLM
            print("Analyzing document with AI...")
            system_prompt = self.create_system_prompt(doc_type, user_query)
            analysis = self.call_llm(cleaned_text, system_prompt)
            
            if not analysis:
                return {
                    "success": False,
                    "error": "Failed to analyze document with LLM"
                }
            
            return {
                "success": True,
                "document_type": doc_type_formatted,
                "analysis": analysis,
                "text_length": len(cleaned_text),
                "filename": Path(file_path).name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def create_document_summariser(
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> DocumentSummariser:
    """Create document summariser with environment defaults."""
    return DocumentSummariser(api_key=api_key, model=model)

    """Analyzes financial documents for rural Indian users using OCR and LLM."""
    
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    MAX_TEXT_LENGTH = 15000
    
    DOCUMENT_PATTERNS = {
        "loan_agreement": [
            r"loan agreement", r"interest rate", r"borrower", 
            r"lender", r"repayment", r"principal amount"
        ],
        "personal_loan": [
            r"personal loan", r"unsecured loan"
        ],
        "mortgage": [
            r"mortgage", r"property", r"collateral"
        ],
        "credit_card": [
            r"credit card", r"annual fee", r"apr"
        ],
        "insurance": [
            r"insurance policy", r"premium", r"coverage"
        ],
        "investment": [
            r"mutual fund", r"sip", r"investment"
        ]
    }
    
    def __init__(self, api_key: str, model: str = "x-ai/grok-4.1-fast:free"):
        """
        Initialize the analyzer with API credentials.
        
        Args:
            api_key: OpenRouter API key
            model: Model identifier to use for analysis
        """
        self.api_key = api_key
        self.model = model
    
    def extract_text(self, file_path: str) -> Optional[str]:
        """
        Extract text from document using PyMuPDF with OCR fallback.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Try direct text extraction first (fast for digital PDFs)
                page_text = page.get_text()
                
                # If text extraction fails or returns very little, use OCR
                if len(page_text.strip()) < 50:
                    # Use PyMuPDF's built-in OCR
                    pix = page.get_pixmap(dpi=300)
                    page_text = page.get_textpage_ocr().extractText()
                
                text += page_text + "\n\n"
            
            doc.close()
            return text if text.strip() else None
            
        except Exception as e:
            print(f"Text extraction error: {str(e)}")
            return None
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw text from OCR
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        # Keep only safe characters
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\₹\%\@\/\n]', '', text)
        # Normalize currency symbols
        text = text.replace('Rs.', '₹').replace('Rs', '₹')
        # Remove page numbers
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def identify_document_type(self, text: str) -> str:
        """
        Identify the type of financial document.
        
        Args:
            text: Cleaned document text
            
        Returns:
            Document type identifier
        """
        text_lower = text.lower()
        scores = {
            doc_type: sum(
                1 for pattern in patterns 
                if re.search(pattern, text_lower, re.IGNORECASE)
            )
            for doc_type, patterns in self.DOCUMENT_PATTERNS.items()
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return "general_financial_document"
        
        return max(scores, key=scores.get)
    
    def create_system_prompt(self, doc_type: str, user_query: Optional[str] = None) -> str:
        """
        Create system prompt for LLM based on document type.
        
        Args:
            doc_type: Type of document identified
            user_query: Optional user query to address
            
        Returns:
            System prompt string
        """
        doc_type_formatted = doc_type.replace('_', ' ').title()
        
        # Extract language instruction if present in user_query
        language_instruction = ""
        cleaned_query = user_query
        if user_query:
            # Check if query starts with language instruction
            if "[Analyze in " in user_query and " language]" in user_query:
                import re
                match = re.search(r'\[Analyze in (.+?) language\]', user_query)
                if match:
                    lang_name = match.group(1)
                    language_instruction = f"IMPORTANT: Provide your ENTIRE response in {lang_name}. All sections (Summary, Important Points, Warnings, Action Points) MUST be in {lang_name}.\n\n"
                    cleaned_query = re.sub(r'\[Analyze in .+? language\]\s*', '', user_query).strip()
        
        base_prompt = f"""{language_instruction}You are a financial advisor helping users understand their financial documents.
The document type is: {doc_type_formatted}

Your task:
1. Provide a SIMPLE summary
2. {'Answer the user query: "' + cleaned_query + '" in simple terms' if cleaned_query else 'Skip to next step'}
3. Identify and explain IMPORTANT POINTS - especially:
   - Hidden charges or penalties
   - High interest rates
   - Confusing terms
   - Any unfair clauses
4. List ACTION POINTS - what the user needs to do
5. WARNINGS - highlight anything that could cause financial harm

Use clear language. Use short sentences. Avoid jargon.
If technical terms are unavoidable, explain them simply.

Format your response clearly with these sections:
- **Summary**
{('- **Answer to Your Question**' if cleaned_query else '')}
- **Important Points**
- **Warnings**
- **Action Points**"""
        
        return base_prompt
    
    def call_llm(self, text: str, system_prompt: str) -> Optional[str]:
        """
        Call LLM API to analyze the document.
        
        Args:
            text: Cleaned document text
            system_prompt: System prompt for the LLM
            
        Returns:
            Analysis result or None if call fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "FinBot-Document-Summariser",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please analyze this financial document:\n\n{text}"}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=data, 
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        
        except requests.exceptions.RequestException as e:
            print(f"API Error: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
    
    def process_document(
        self, 
        file_path: str, 
        user_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a financial document through the complete pipeline.
        
        Args:
            file_path: Path to the document file
            user_query: Optional user query to answer
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Step 1: Extract text using OCR
            print("Extracting text from document...")
            raw_text = self.extract_text(file_path)
            if not raw_text:
                return {
                    "success": False,
                    "error": "Failed to extract text from document"
                }
            
            # Step 2: Clean the extracted text
            print("Cleaning extracted text...")
            cleaned_text = self.clean_text(raw_text)
            
            if len(cleaned_text) > self.max_text_length:
                cleaned_text = cleaned_text[:self.max_text_length] + "\n\n[Document truncated for analysis]"
            
            # Step 3: Identify document type
            doc_type = self.identify_document_type(cleaned_text)
            doc_type_formatted = doc_type.replace('_', ' ').title()
            
            # Step 4: Analyze with LLM
            print("Analyzing document with AI...")
            system_prompt = self.create_system_prompt(doc_type, user_query)
            analysis = self.call_llm(cleaned_text, system_prompt)
            
            if not analysis:
                return {
                    "success": False,
                    "error": "Failed to analyze document with LLM"
                }
            
            return {
                "success": True,
                "document_type": doc_type_formatted,
                "analysis": analysis,
                "text_length": len(cleaned_text),
                "filename": Path(file_path).name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def create_document_summariser(
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> DocumentSummariser:
    """Create document summariser with environment defaults."""
    return DocumentSummariser(api_key=api_key, model=model)


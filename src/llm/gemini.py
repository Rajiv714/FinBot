"""
Gemini LLM service for financial assistance.
"""

import os
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GeminiLLMService:
    """Financial assistant using Google Gemini."""
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash",  # Changed to match .env default
        temperature: float = 0.1,
        max_tokens: int = 1024  # Changed to match .env default
    ):
        # Store configuration for system status
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Generation config
        self.config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
    
    def generate_response(self, query: str = None, context: Optional[str] = None, prompt: str = None) -> str:
        """Generate response for financial query or direct prompt."""
        try:
            # Support both new interface (query + context) and legacy interface (prompt)
            if prompt is not None:
                # Legacy interface: direct prompt
                final_prompt = prompt
            else:
                # New interface: build prompt from query and context
                final_prompt = self._build_prompt(query, context)
            
            response = self.model.generate_content(final_prompt, generation_config=self.config)
            
            if response.text:
                return response.text.strip()
            else:
                return "I couldn't generate a response. Please try rephrasing your question."
                
        except Exception as e:
            # Log the actual error for debugging
            print(f"ERROR in Gemini LLM: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"I'm experiencing technical difficulties: {str(e)}"
    
    def _build_prompt(self, query: str, context: Optional[str] = None) -> str:
        """Build optimized prompt for financial queries."""
        
        if context:
            # Keep context reasonable but useful
            if len(context) > 3000:
                context = context[:3000] + "..."
            
            return f"""You are a knowledgeable financial advisor. Based on the provided information, give a clear and helpful answer.

Financial Information:
{context}

User Question: {query}

Please provide a practical answer that helps the user understand the topic. Use simple language and include specific details when helpful."""

        else:
            return f"""You are a knowledgeable financial advisor. Answer this question with clear, practical advice.

User Question: {query}

Please provide a helpful answer using your knowledge of finance and investments. Use simple language that anyone can understand."""


def create_gemini_service(
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> GeminiLLMService:
    """Create Gemini service with environment defaults."""
    
    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
    
    model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    temperature = temperature if temperature is not None else float(os.getenv("TEMPERATURE", "0.1"))
    max_tokens = max_tokens if max_tokens is not None else int(os.getenv("MAX_TOKENS", "1024"))
    
    return GeminiLLMService(
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )

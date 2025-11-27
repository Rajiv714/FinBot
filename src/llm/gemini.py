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
        max_tokens: int = 2048  # Increased for longer handouts (1200+ words)
    ):
        # Store configuration for system status
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Safety settings - More permissive for financial education content
        safety_settings = {
            "HARASSMENT": "BLOCK_NONE",
            "HATE_SPEECH": "BLOCK_NONE",
            "SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "DANGEROUS_CONTENT": "BLOCK_NONE"
        }
        
        self.model = genai.GenerativeModel(
            model_name,
            safety_settings=safety_settings
        )
        
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
            
            # Debug: Print prompt details
            print(f"\n{'='*60}")
            print(f"DEBUG GEMINI API CALL:")
            print(f"  Query: {query[:100] if query else 'None'}...")
            print(f"  Context chars: {len(context) if context else 0}")
            print(f"  Context words: ~{len(context) // 5 if context else 0}")
            print(f"  Final prompt chars: {len(final_prompt)}")
            print(f"  Final prompt words: ~{len(final_prompt) // 5}")
            print(f"  Estimated tokens: ~{len(final_prompt) // 4}")
            print(f"{'='*60}\n")
            
            response = self.model.generate_content(final_prompt, generation_config=self.config)
            
            # Debug: Print response details
            print(f"\n{'='*60}")
            print(f"DEBUG GEMINI RESPONSE:")
            print(f"  Response candidates: {len(response.candidates)}")
            if response.candidates:
                print(f"  Finish reason: {response.candidates[0].finish_reason}")
                print(f"  Safety ratings: {response.candidates[0].safety_ratings}")
            print(f"{'='*60}\n")
            
            # Check if response has valid text
            try:
                if response.text:
                    return response.text.strip()
            except ValueError as ve:
                # Handle blocked/filtered responses (finish_reason=2 or other issues)
                finish_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
                
                print(f"DEBUG - ValueError caught. Finish reason: {finish_reason}")
                print(f"DEBUG - Prompt feedback: {response.prompt_feedback}")
                
                if "finish_reason" in str(ve) or finish_reason == 2:
                    # Response was blocked by safety filters
                    return "I apologize, but I couldn't generate a response for this query. This might be due to content safety filters. Please try rephrasing your question or asking about a different financial topic."
                else:
                    # Other ValueError
                    return f"I encountered an issue generating a response. Please try again with a different question."
            
            # If no text and no exception, return generic message
            return "I couldn't generate a response. Please try rephrasing your question."
                
        except Exception as e:
            # Log the actual error for debugging
            print(f"ERROR in Gemini LLM: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"I'm experiencing technical difficulties: {str(e)}"
    
    def _build_prompt(self, query: str, context: Optional[str] = None) -> str:
        """Build optimized prompt for financial queries - Balanced for quality and tokens."""
        
        if context:
            # Allow more context for better answers - Gemini can handle it
            # Up to 10,000 chars (~2000 words, ~2500 tokens) for quality answers
            if len(context) > 10000:
                context = context[:10000] + "..."
            
            return f"""You are a helpful financial advisor. Use the following information to answer the question clearly and comprehensively.

Context:
{context}

Question: {query}

Instructions:
- Provide a clear, well-structured answer based on the context above
- Use bullet points or numbered lists where appropriate
- Explain concepts in simple language
- Include relevant examples or details from the context
- Break down complex topics into easy-to-understand sections
- If the context doesn't fully answer the question, mention what information is available

Answer:"""

        else:
            return f"""You are a helpful financial advisor. Answer the following question clearly and comprehensively.

Question: {query}

Answer:"""


def create_gemini_service(
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    use_case: str = "chat"  # "chat" or "handout"
) -> GeminiLLMService:
    """Create Gemini service with environment defaults.
    
    Args:
        api_key: Gemini API key
        model_name: Model name to use
        temperature: Generation temperature
        max_tokens: Max output tokens
        use_case: "chat" for chatbot (shorter, faster) or "handout" for long-form content
    """
    
    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
    
    model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    temperature = temperature if temperature is not None else float(os.getenv("TEMPERATURE", "0.1"))
    
    # Different defaults based on use case
    if max_tokens is None:
        if use_case == "handout":
            # Handout needs 1200+ words = ~1600 tokens minimum
            max_tokens = int(os.getenv("MAX_TOKENS_HANDOUT", "2048"))
        else:
            # Chat needs quick, concise responses
            max_tokens = int(os.getenv("MAX_TOKENS_CHAT", "1024"))
    
    return GeminiLLMService(
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return GeminiLLMService(
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )

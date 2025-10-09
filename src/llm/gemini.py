"""
Simple Gemini LLM service for response generation.
"""

import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai


class GeminiLLMService:
    """Simple service for generating responses using Google Gemini."""
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash-exp",
        temperature: float = 0.1,
        max_tokens: int = 1024
    ):
        """
        Initialize the Gemini LLM service.
        
        Args:
            api_key: Google AI API key
            model_name: Gemini model name
            temperature: Temperature for sampling
            max_tokens: Maximum token length for generation
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(model_name)
        
        # Set up generation config
        self.generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
    
    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate response from the model.
        
        Args:
            prompt: User query/prompt
            context: Optional context from retrieval
            max_tokens: Override max tokens for this generation
            temperature: Override temperature for this generation
            
        Returns:
            Generated response text
        """
        try:
            # Format prompt with context
            formatted_prompt = self._format_prompt(prompt, context)
            
            # Override generation config if needed
            config = self.generation_config
            if max_tokens is not None or temperature is not None:
                config = genai.GenerationConfig(
                    temperature=temperature if temperature is not None else self.temperature,
                    max_output_tokens=max_tokens if max_tokens is not None else self.max_tokens,
                )
            
            # Generate response
            response = self.model.generate_content(
                formatted_prompt,
                generation_config=config
            )
            
            return response.text.strip()
                
        except Exception as e:
            return f"I apologize, but I encountered an error while generating a response: {str(e)}"
    
    def _format_prompt(self, query: str, context: Optional[str] = None) -> str:
        """
        Format the prompt with context for financial Q&A.
        
        Args:
            query: User question
            context: Retrieved context from documents
            
        Returns:
            Formatted prompt string
        """
        system_prompt = """You are a helpful financial literacy assistant. Provide accurate, clear, and educational responses about financial topics. Use simple language that's easy to understand. Focus on financial education and literacy."""

        if context:
            prompt = f"""{system_prompt}

Context from financial documents:
{context}

Question: {query}

Please provide a helpful and accurate answer based on the context provided and your knowledge of financial topics."""
        else:
            prompt = f"""{system_prompt}

Question: {query}

Please provide a helpful and accurate answer about this financial topic."""
        
        return prompt
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate response for chat-style interaction.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Override max tokens
            temperature: Override temperature
            
        Returns:
            Generated response
        """
        try:
            # Convert messages to a simple conversation format
            conversation_parts = []
            
            for message in messages:
                role = message.get("role", "user")
                content = message.get("content", "")
                
                if role == "user":
                    conversation_parts.append(f"User: {content}")
                elif role == "assistant":
                    conversation_parts.append(f"Assistant: {content}")
                elif role == "system":
                    conversation_parts.append(f"System: {content}")
            
            # Add the current context for financial assistant
            conversation_text = "\n".join(conversation_parts)
            prompt = f"""You are a helpful financial literacy assistant. Here's our conversation so far:

{conversation_text}

Please continue the conversation by providing a helpful response to the user's latest question. Focus on financial education and use simple, clear language."""
            
            # Override generation config if needed
            config = self.generation_config
            if max_tokens is not None or temperature is not None:
                config = genai.GenerationConfig(
                    temperature=temperature if temperature is not None else self.temperature,
                    max_output_tokens=max_tokens if max_tokens is not None else self.max_tokens,
                )
            
            response = self.model.generate_content(prompt, generation_config=config)
            return response.text.strip()
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"


def create_gemini_service(
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> GeminiLLMService:
    """
    Factory function to create Gemini service with environment variables.
    
    Args:
        api_key: Gemini API key (uses env variable if None)
        model_name: Model name (uses env variable if None)
        temperature: Temperature (uses env variable if None)
        max_tokens: Max tokens (uses env variable if None)
        
    Returns:
        Configured GeminiLLMService instance
    """
    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
    
    if model_name is None:
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    if temperature is None:
        temperature = float(os.getenv("TEMPERATURE", "0.1"))
    
    if max_tokens is None:
        max_tokens = int(os.getenv("MAX_TOKENS", "1024"))
    
    return GeminiLLMService(
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )

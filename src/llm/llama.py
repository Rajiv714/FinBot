"""
Simple local LLM service using Llama 3.1 8B model.
"""

import os
from typing import List, Dict, Any, Optional
import torch
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    GenerationConfig
)


class LlamaLLMService:
    """Simple service for generating responses using Llama 3.1 8B model."""
    
    def __init__(
        self,
        model_path: str,
        max_length: int = 1024,
        temperature: float = 0.1
    ):
        """
        Initialize the Llama LLM service.
        
        Args:
            model_path: Path to the Llama model directory
            max_length: Maximum token length for generation
            temperature: Temperature for sampling
        """
        self.model_path = model_path
        self.max_length = max_length
        self.temperature = temperature
        
        # Auto-detect device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load model and tokenizer
        self._load_model()
        
        # Set up generation config
        self._setup_generation_config()
    
    def _load_model(self):
        """Load the Llama model and tokenizer."""
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                padding_side="left"
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "device_map": "auto" if self.device == "cuda" else None,
                "low_cpu_mem_usage": True,
            }
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                **model_kwargs
            )
            
            # Move to device if not using device_map
            if model_kwargs.get("device_map") is None:
                self.model = self.model.to(self.device)
                
        except Exception as e:
            raise RuntimeError(f"Could not load Llama model: {str(e)}")
    
    def _setup_generation_config(self):
        """Set up generation configuration."""
        self.generation_config = GenerationConfig(
            max_new_tokens=self.max_length,
            temperature=self.temperature,
            top_p=0.9,
            do_sample=True if self.temperature > 0 else False,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            repetition_penalty=1.1,
            use_cache=True
        )
    
    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate response from the model.
        
        Args:
            prompt: User query/prompt
            context: Optional context from retrieval
            max_new_tokens: Override max tokens for this generation
            temperature: Override temperature for this generation
            
        Returns:
            Generated response text
        """
        try:
            # Format prompt with context
            formatted_prompt = self._format_prompt(prompt, context)
            
            return self._generate_batch(formatted_prompt, max_new_tokens, temperature)
                
        except Exception as e:
            return "I apologize, but I encountered an error while generating a response. Please try again."
    
    def _generate_batch(
        self,
        formatted_prompt: str,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate response in batch mode."""
        # Tokenize input
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096 - (max_new_tokens or self.max_length)
        ).to(self.device)
        
        # Override generation config if needed
        gen_config = self.generation_config
        if max_new_tokens is not None or temperature is not None:
            gen_config = GenerationConfig(**gen_config.to_dict())
            if max_new_tokens is not None:
                gen_config.max_new_tokens = max_new_tokens
            if temperature is not None:
                gen_config.temperature = temperature
                gen_config.do_sample = temperature > 0
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                generation_config=gen_config,
                return_dict_in_generate=True,
                output_scores=False
            )
        
        # Decode response
        generated_tokens = outputs.sequences[0][inputs.input_ids.shape[1]:]
        response = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
        return response.strip()
    
    def _format_prompt(self, query: str, context: Optional[str] = None) -> str:
        """
        Format the prompt with context for financial Q&A.
        
        Args:
            query: User question
            context: Retrieved context from documents
            
        Returns:
            Formatted prompt string
        """
        system_prompt = """You are a helpful financial literacy assistant. Provide accurate, clear, and educational responses about financial topics. Use simple language that's easy to understand."""

        if context:
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

Context from financial documents:
{context}

Question: {query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        else:
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        return prompt
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate response for chat-style interaction.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_new_tokens: Override max tokens
            temperature: Override temperature
            
        Returns:
            Generated response
        """
        # Convert messages to prompt format
        prompt_parts = ["<|begin_of_text|>"]
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            prompt_parts.append(f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}<|eot_id|>")
        
        prompt_parts.append("<|start_header_id|>assistant<|end_header_id|>\n\n")
        formatted_prompt = "".join(prompt_parts)
        
        return self._generate_batch(formatted_prompt, max_new_tokens, temperature)


def create_llama_service(
    model_path: str = "/home/rajiv07/Chatbots/Llama-3.1-8B",
    **kwargs
) -> LlamaLLMService:
    """
    Factory function to create Llama service.
    
    Args:
        model_path: Path to model
        **kwargs: Additional arguments for LlamaLLMService
        
    Returns:
        Configured LlamaLLMService instance
    """
    return LlamaLLMService(model_path=model_path, **kwargs)
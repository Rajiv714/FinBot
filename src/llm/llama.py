"""
Local LLM service using Llama 3.1 8B model for response generation.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Generator
import torch
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    GenerationConfig,
    TextStreamer
)
from accelerate import Accelerator


class LlamaLLMService:
    """Service for generating responses using Llama 3.1 8B model."""
    
    def __init__(
        self,
        model_path: str,
        device: Optional[str] = None,
        max_length: int = 4096,
        temperature: float = 0.1,
        top_p: float = 0.9,
        top_k: int = 50
    ):
        """
        Initialize the Llama LLM service.
        
        Args:
            model_path: Path to the Llama model directory
            device: Device to run model on (auto-detected if None)
            max_length: Maximum token length for generation
            temperature: Temperature for sampling
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
        """
        self.logger = logging.getLogger(__name__)
        self.model_path = model_path
        self.max_length = max_length
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.logger.info(f"Using device: {self.device}")
        
        # Initialize accelerator for better device management
        self.accelerator = Accelerator()
        
        # Load model and tokenizer
        self._load_model()
        
        # Set up generation config
        self._setup_generation_config()
    
    def _load_model(self):
        """Load the Llama model and tokenizer."""
        try:
            self.logger.info(f"Loading Llama model from: {self.model_path}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                padding_side="left"
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with optimal settings
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "device_map": "auto" if self.device == "cuda" else None,
                "low_cpu_mem_usage": True,
            }
            
            # Add quantization if available and on CUDA
            if self.device == "cuda":
                try:
                    from transformers import BitsAndBytesConfig
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4"
                    )
                    model_kwargs["quantization_config"] = quantization_config
                    self.logger.info("Using 4-bit quantization")
                except ImportError:
                    self.logger.info("BitsAndBytesConfig not available, loading without quantization")
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                **model_kwargs
            )
            
            # Move to device if not using device_map
            if model_kwargs.get("device_map") is None:
                self.model = self.model.to(self.device)
            
            # Prepare with accelerator
            self.model, self.tokenizer = self.accelerator.prepare(self.model, self.tokenizer)
            
            self.logger.info("Llama model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load Llama model: {str(e)}")
            raise RuntimeError(f"Could not load Llama model: {str(e)}")
    
    def _setup_generation_config(self):
        """Set up generation configuration."""
        self.generation_config = GenerationConfig(
            max_new_tokens=self.max_length,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            do_sample=True if self.temperature > 0 else False,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            repetition_penalty=1.1,
            length_penalty=1.0,
            use_cache=True
        )
    
    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> str:
        """
        Generate response from the model.
        
        Args:
            prompt: User query/prompt
            context: Optional context from retrieval
            max_new_tokens: Override max tokens for this generation
            temperature: Override temperature for this generation
            stream: Whether to stream the response
            
        Returns:
            Generated response text
        """
        try:
            # Format prompt with context
            formatted_prompt = self._format_prompt(prompt, context)
            
            if stream:
                return self._generate_streaming(formatted_prompt, max_new_tokens, temperature)
            else:
                return self._generate_batch(formatted_prompt, max_new_tokens, temperature)
                
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
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
    
    def _generate_streaming(
        self,
        formatted_prompt: str,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Generator[str, None, None]:
        """Generate response in streaming mode."""
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
        
        # Create streamer
        streamer = TextStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        # Generate with streaming
        with torch.no_grad():
            self.model.generate(
                **inputs,
                generation_config=gen_config,
                streamer=streamer
            )
    
    def _format_prompt(self, query: str, context: Optional[str] = None) -> str:
        """
        Format the prompt with context for financial Q&A.
        
        Args:
            query: User question
            context: Retrieved context from documents
            
        Returns:
            Formatted prompt string
        """
        system_prompt = """You are a helpful financial literacy assistant. Your role is to provide accurate, clear, and educational responses about financial topics. Use the provided context to answer questions, but also draw from your knowledge when helpful.

Guidelines:
- Provide accurate and helpful financial information
- Use simple language that's easy to understand
- Include practical examples when relevant
- If you're unsure about something, say so
- Focus on financial literacy and education
- Be objective and avoid giving specific investment advice"""

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
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model_path": self.model_path,
            "device": str(self.device),
            "model_type": type(self.model).__name__,
            "vocab_size": len(self.tokenizer),
            "max_length": self.max_length,
            "temperature": self.temperature
        }


def create_llama_service(
    model_path: Optional[str] = None,
    device: Optional[str] = None,
    **kwargs
) -> LlamaLLMService:
    """
    Factory function to create Llama service with environment variables.
    
    Args:
        model_path: Path to model (uses env variable if None)
        device: Device to use (auto-detected if None)
        **kwargs: Additional arguments for LlamaLLMService
        
    Returns:
        Configured LlamaLLMService instance
    """
    if model_path is None:
        model_path = os.getenv("LLAMA_MODEL_PATH", "./Llama-3.1-8B")
    
    # Get other parameters from environment
    max_length = int(os.getenv("MAX_TOKENS", "4096"))
    temperature = float(os.getenv("TEMPERATURE", "0.1"))
    
    return LlamaLLMService(
        model_path=model_path,
        device=device,
        max_length=max_length,
        temperature=temperature,
        **kwargs
    )
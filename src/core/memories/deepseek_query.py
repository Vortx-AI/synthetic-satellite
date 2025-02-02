from vllm import LLM, SamplingParams
from typing import List, Optional, Dict, Union
import logging
from datetime import datetime
import json
import torch

class DeepSeekVLLM:
    def __init__(
        self,
        model_name: str = "deepseek-ai/deepseek-coder-1.3b-base",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 0.95,
        tensor_parallel_size: int = 1,
        verbose: bool = False
    ):
        """
        Initialize DeepSeek with vLLM
        
        Args:
            model_name: Name or path of the model
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            top_p: Top-p sampling parameter
            tensor_parallel_size: Number of GPUs for tensor parallelism
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self._setup_logging()
        
        self.logger.info(f"Initializing DeepSeek with vLLM using model: {model_name}")
        
        # Initialize vLLM model
        self.model = LLM(
            model=model_name,
            tensor_parallel_size=tensor_parallel_size,
            trust_remote_code=True
        )
        
        # Set default sampling parameters
        self.sampling_params = SamplingParams(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p
        )
        
        self.conversation_history = []
        
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def generate(
        self,
        prompt: str,
        sampling_params: Optional[SamplingParams] = None
    ) -> str:
        """
        Generate response for a single prompt
        
        Args:
            prompt: Input prompt
            sampling_params: Optional custom sampling parameters
            
        Returns:
            Generated response
        """
        try:
            params = sampling_params or self.sampling_params
            outputs = self.model.generate([prompt], params)
            response = outputs[0].outputs[0].text
            
            # Store in conversation history
            self.conversation_history.append({
                "prompt": prompt,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error during generation: {str(e)}")
            raise
            
    def batch_generate(
        self,
        prompts: List[str],
        sampling_params: Optional[SamplingParams] = None
    ) -> List[str]:
        """
        Generate responses for multiple prompts in parallel
        
        Args:
            prompts: List of input prompts
            sampling_params: Optional custom sampling parameters
            
        Returns:
            List of generated responses
        """
        try:
            params = sampling_params or self.sampling_params
            outputs = self.model.generate(prompts, params)
            responses = [output.outputs[0].text for output in outputs]
            
            # Store in conversation history
            for prompt, response in zip(prompts, responses):
                self.conversation_history.append({
                    "prompt": prompt,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                
            return responses
            
        except Exception as e:
            self.logger.error(f"Error during batch generation: {str(e)}")
            raise
            
    def save_history(self, filepath: str):
        """Save conversation history to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2)
            self.logger.info(f"Conversation history saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving history: {str(e)}")
            raise
            
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.logger.info("Conversation history cleared")
        
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history

# Example usage
if __name__ == "__main__":
    # Initialize DeepSeek with vLLM
    deepseek = DeepSeekVLLM(verbose=True)
    
    # Single prompt example
    prompt = """
    Write a Python function to implement binary search.
    Include comments and example usage.
    """
    
    response = deepseek.generate(prompt)
    print(f"\nResponse:\n{response}")
    
    # Batch processing example
    prompts = [
        "Explain what is a neural network",
        "Write a function to sort a list in Python",
        "What are the benefits of using vLLM?"
    ]
    
    responses = deepseek.batch_generate(prompts)
    
    for prompt, response in zip(prompts, responses):
        print(f"\nPrompt: {prompt}")
        print(f"Response: {response}")
        
    # Save conversation history
    deepseek.save_history("conversation_history.json")
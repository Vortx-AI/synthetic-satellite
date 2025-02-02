from vllm import LLM, SamplingParams
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
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
        verbose: bool = False
    ):
        """
        Initialize DeepSeek with vLLM
        
        Args:
            model_name: Name or path of the model
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            top_p: Top-p sampling parameter
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self._setup_logging()
        
        self.logger.info(f"Initializing DeepSeek with vLLM using model: {model_name}")
        
        # Initialize vLLM with conservative memory settings
        self.model = LLM(
            model=model_name,
            trust_remote_code=True,
            tensor_parallel_size=1,
            dtype="float16",  # For T4 GPU compatibility
            max_model_len=2048,  # Conservative sequence length
            gpu_memory_utilization=0.8,  # Conservative memory usage
            enforce_eager=True  # Disable CUDA graphs for better compatibility
        )
        
        # Store sampling parameters
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
        template: Optional[str] = None
    ) -> str:
        """
        Generate response for a single prompt
        
        Args:
            prompt: Input prompt
            template: Optional prompt template
            
        Returns:
            Generated response
        """
        try:
            if template:
                # Use template if provided
                prompt_template = PromptTemplate(
                    input_variables=["query"],
                    template=template
                )
                formatted_prompt = prompt_template.format(query=prompt)
            else:
                formatted_prompt = prompt
            
            # Generate response using vLLM directly
            outputs = self.model.generate(formatted_prompt, self.sampling_params)
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
        template: Optional[str] = None
    ) -> List[str]:
        """
        Generate responses for multiple prompts
        
        Args:
            prompts: List of input prompts
            template: Optional prompt template
            
        Returns:
            List of generated responses
        """
        try:
            if template:
                prompt_template = PromptTemplate(
                    input_variables=["query"],
                    template=template
                )
                formatted_prompts = [prompt_template.format(query=p) for p in prompts]
            else:
                formatted_prompts = prompts
            
            # Generate responses using vLLM directly
            outputs = self.model.generate(formatted_prompts, self.sampling_params)
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

def query_llm(prompt: str, model_name: str = "deepseek-ai/deepseek-coder-1.3b-base") -> str:
    """
    Simple function to query the LLM with a single prompt
    
    Args:
        prompt: The input prompt to send to the model
        model_name: Optional model name/path (defaults to deepseek-coder-1.3b-base)
        
    Returns:
        str: The model's response
    """
    try:
        llm = DeepSeekVLLM(model_name=model_name)
        response = llm.generate(prompt)
        return response
    except Exception as e:
        logging.error(f"Error querying LLM: {str(e)}")
        raise


from langchain_community.llms import VLLMOpenAI
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import List, Optional, Dict, Union
import logging
from datetime import datetime
import json

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
        Initialize DeepSeek with LangChain and vLLM
        
        Args:
            model_name: Name or path of the model
            temperature: Sampling temperature
            max_tokens: Maximum number of tokens to generate
            top_p: Top-p sampling parameter
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self._setup_logging()
        
        self.logger.info(f"Initializing DeepSeek with LangChain using model: {model_name}")
        
        # Setup callback manager for streaming output
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        
        # Initialize LangChain VLLM wrapper
        self.model = VLLMOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            model_kwargs={"dtype": "float16"},  # For T4 compatibility
            callback_manager=callback_manager if verbose else None,
            verbose=verbose
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
                # Use LangChain's PromptTemplate if template is provided
                prompt_template = PromptTemplate(
                    input_variables=["query"],
                    template=template
                )
                chain = LLMChain(llm=self.model, prompt=prompt_template)
                response = chain.run(query=prompt)
            else:
                # Direct generation if no template
                response = self.model(prompt)
            
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
                chain = LLMChain(llm=self.model, prompt=prompt_template)
                responses = [chain.run(query=prompt) for prompt in prompts]
            else:
                responses = self.model.generate(prompts)
            
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
    # Initialize DeepSeek with LangChain
    deepseek = DeepSeekVLLM(verbose=True)
    
    # Example with a simple prompt
    prompt = "Write a Python function to implement binary search."
    response = deepseek.generate(prompt)
    print(f"\nDirect Response:\n{response}")
    
    # Example with a template
    template = """
    You are an expert Python programmer. Please help with the following task:
    
    {query}
    
    Please provide a detailed solution with comments and example usage.
    """
    
    response = deepseek.generate(
        prompt="Implement a function to find the longest common subsequence of two strings.",
        template=template
    )
    print(f"\nTemplate Response:\n{response}")
    
    # Batch processing example
    prompts = [
        "Explain what is a neural network",
        "Write a function to sort a list in Python",
        "What are the benefits of using LangChain?"
    ]
    
    responses = deepseek.batch_generate(prompts)
    
    for prompt, response in zip(prompts, responses):
        print(f"\nPrompt: {prompt}")
        print(f"Response: {response}")
        
    # Save conversation history
    deepseek.save_history("conversation_history.json")
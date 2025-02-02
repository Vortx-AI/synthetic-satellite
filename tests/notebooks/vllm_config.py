"""Configuration for DeepSeek vLLM"""

VLLM_CONFIG = {
    "model": {
        "name": "deepseek-ai/deepseek-coder-1.3b-base",
        "tensor_parallel_size": 1  # Increase for multi-GPU setup
    },
    "generation": {
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 0.95,
        "top_k": 50,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0
    },
    "prompts": {
        "code": """
        Write code for the following task:
        {query}
        
        Provide:
        1. Implementation
        2. Comments
        3. Example usage
        """,
        "explanation": """
        Explain the following concept:
        {query}
        
        Include:
        1. Definition
        2. Key points
        3. Examples
        """,
        "analysis": """
        Analyze the following:
        {query}
        
        Consider:
        1. Main aspects
        2. Advantages/disadvantages
        3. Practical implications
        """
    }
}
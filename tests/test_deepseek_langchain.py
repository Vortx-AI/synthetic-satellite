import unittest
from langchain.llms import DeepSeek
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestDeepSeekLangChain(unittest.TestCase):
    def setUp(self):
        """Initialize DeepSeek and basic components"""
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.llm = DeepSeek(
            api_key=self.api_key,
            model_name="deepseek-chat",
            temperature=0.7
        )
        
        # Initialize basic prompt template
        self.basic_prompt = PromptTemplate(
            input_variables=["query"],
            template="Please analyze the following: {query}"
        )
        
        # Initialize memory
        self.memory = ConversationBufferMemory()
        
    def test_basic_query(self):
        """Test basic query functionality"""
        chain = LLMChain(llm=self.llm, prompt=self.basic_prompt)
        response = chain.run("What is machine learning?")
        
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
        
    def test_memory_retention(self):
        """Test conversation memory functionality"""
        prompt_template = PromptTemplate(
            input_variables=["history", "query"],
            template="Context: {history}\nCurrent Query: {query}"
        )
        
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt_template,
            memory=self.memory
        )
        
        # First query
        response1 = chain.run("What is deep learning?")
        # Follow-up query
        response2 = chain.run("How does it differ from machine learning?")
        
        self.assertIsInstance(response2, str)
        self.assertTrue(len(response2) > 0)
        
    def test_temperature_variation(self):
        """Test different temperature settings"""
        # Create two instances with different temperatures
        llm_creative = DeepSeek(
            api_key=self.api_key,
            model_name="deepseek-chat",
            temperature=0.9
        )
        
        llm_precise = DeepSeek(
            api_key=self.api_key,
            model_name="deepseek-chat",
            temperature=0.1
        )
        
        prompt = PromptTemplate(
            input_variables=["query"],
            template="Generate a creative description: {query}"
        )
        
        chain_creative = LLMChain(llm=llm_creative, prompt=prompt)
        chain_precise = LLMChain(llm=llm_precise, prompt=prompt)
        
        response_creative = chain_creative.run("Describe a sunset")
        response_precise = chain_precise.run("Describe a sunset")
        
        self.assertNotEqual(response_creative, response_precise)
        
    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        chain = LLMChain(llm=self.llm, prompt=self.basic_prompt)
        
        with self.assertRaises(Exception):
            chain.run("")  # Empty query
            
    def test_structured_output(self):
        """Test structured output formatting"""
        structured_prompt = PromptTemplate(
            input_variables=["topic"],
            template="""
            Provide a structured analysis of {topic} with:
            1. Definition
            2. Key components
            3. Applications
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=structured_prompt)
        response = chain.run("artificial intelligence")
        
        self.assertIn("Definition", response)
        self.assertIn("Key components", response)
        self.assertIn("Applications", response)

if __name__ == "__main__":
    unittest.main()
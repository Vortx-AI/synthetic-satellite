import os
import sys
import unittest
from pathlib import Path
import json
import shutil
import tempfile
from PIL import Image
import numpy as np
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
project_root=os.getenv('PROJECT_ROOT')

# Add project root to Python path
#project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.memories.deepseek_image_rag import DeepSeekImageRAG

class TestDeepSeekImageRAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests"""
        # Create temporary directory for test files
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_data_dir = os.path.join(cls.temp_dir, 'test_data')
        os.makedirs(cls.test_data_dir, exist_ok=True)
        
        # Create test images
        cls.create_test_images()
        
        # Create test knowledge bases
        cls.create_test_knowledge_bases()
        
        # Initialize RAG system
        cls.rag = DeepSeekImageRAG(
            model_name="deepseek-ai/deepseek-coder-1.3b-base",
            embedding_model="BAAI/bge-large-en-v1.5",
            image_embedding_model="openai/clip-vit-base-patch32",
            verbose=True
        )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        # Remove temporary directory and all its contents
        shutil.rmtree(cls.temp_dir)
    
    @classmethod
    def create_test_images(cls):
        """Create test images for testing"""
        # Create a few test images with different colors
        images = {
            'red.jpg': (255, 0, 0),
            'green.jpg': (0, 255, 0),
            'blue.jpg': (0, 0, 255)
        }
        
        cls.image_paths = {}
        for filename, color in images.items():
            # Create a small colored image
            img = Image.new('RGB', (100, 100), color)
            path = os.path.join(cls.test_data_dir, filename)
            img.save(path)
            cls.image_paths[filename] = path
    
    @classmethod
    def create_test_knowledge_bases(cls):
        """Create test knowledge base files"""
        # Create text knowledge base
        cls.text_kb_path = os.path.join(cls.test_data_dir, 'text_kb.json')
        text_kb = {
            "documents": [
                {
                    "content": "This is a test document about a red object.",
                    "metadata": {"type": "color", "subject": "red"}
                },
                {
                    "content": "Here's information about a green item.",
                    "metadata": {"type": "color", "subject": "green"}
                },
                {
                    "content": "Description of a blue element.",
                    "metadata": {"type": "color", "subject": "blue"}
                }
            ]
        }
        with open(cls.text_kb_path, 'w') as f:
            json.dump(text_kb, f)
        
        # Create image knowledge base
        cls.image_kb_path = os.path.join(cls.test_data_dir, 'image_kb.json')
        image_kb = {
            "images": [
                {
                    "path": cls.image_paths['red.jpg'],
                    "metadata": {"type": "color", "subject": "red"}
                },
                {
                    "path": cls.image_paths['green.jpg'],
                    "metadata": {"type": "color", "subject": "green"}
                },
                {
                    "path": cls.image_paths['blue.jpg'],
                    "metadata": {"type": "color", "subject": "blue"}
                }
            ]
        }
        with open(cls.image_kb_path, 'w') as f:
            json.dump(image_kb, f)
    
    def test_initialization(self):
        """Test if RAG system initializes correctly"""
        self.assertIsNotNone(self.rag)
        self.assertIsNotNone(self.rag.model)
        self.assertIsNotNone(self.rag.text_embedding_model)
        self.assertIsNotNone(self.rag.clip_model)
        self.assertIsNotNone(self.rag.clip_processor)
    
    def test_load_knowledge_bases(self):
        """Test loading of knowledge bases"""
        try:
            self.rag.load_text_knowledge_base(self.text_kb_path)
            self.rag.load_image_knowledge_base(self.image_kb_path)
            
            # Verify text vector store
            self.assertIsNotNone(self.rag.text_vector_store)
            
            # Verify image vector store
            self.assertIsNotNone(self.rag.image_vector_store)
        except Exception as e:
            self.fail(f"Loading knowledge bases failed with error: {str(e)}")
    
    def test_search(self):
        """Test search functionality"""
        # Ensure knowledge bases are loaded
        if self.rag.text_vector_store is None:
            self.rag.load_text_knowledge_base(self.text_kb_path)
        if self.rag.image_vector_store is None:
            self.rag.load_image_knowledge_base(self.image_kb_path)
        
        # Test search
        query = "red"
        results = self.rag.search(query)
        
        # Verify results structure
        self.assertIn("texts", results)
        self.assertIn("images", results)
        
        # Verify we got some results
        self.assertTrue(len(results["texts"]) > 0)
        self.assertTrue(len(results["images"]) > 0)
    
    def test_generate_answer(self):
        """Test answer generation"""
        # Ensure knowledge bases are loaded
        if self.rag.text_vector_store is None:
            self.rag.load_text_knowledge_base(self.text_kb_path)
        if self.rag.image_vector_store is None:
            self.rag.load_image_knowledge_base(self.image_kb_path)
        
        # Test generation
        query = "What can you tell me about the red object?"
        answer = self.rag.generate_answer(query)
        
        # Verify we got a non-empty answer
        self.assertIsNotNone(answer)
        self.assertTrue(len(answer) > 0)
    
    def test_error_handling(self):
        """Test error handling for various scenarios"""
        # Test with non-existent knowledge base file
        with self.assertRaises(Exception):
            self.rag.load_text_knowledge_base("nonexistent.json")
        
        # Test with invalid image path
        invalid_image_kb = {
            "images": [
                {
                    "path": "nonexistent.jpg",
                    "metadata": {"type": "invalid"}
                }
            ]
        }
        invalid_kb_path = os.path.join(self.test_data_dir, 'invalid_kb.json')
        with open(invalid_kb_path, 'w') as f:
            json.dump(invalid_image_kb, f)
        
        # Should log warning but not raise exception
        self.rag.load_image_knowledge_base(invalid_kb_path)
    
    def test_vector_store_persistence(self):
        """Test saving and loading vector stores"""
        # Create paths for vector store indices
        text_index_path = os.path.join(self.test_data_dir, 'text_index')
        image_index_path = os.path.join(self.test_data_dir, 'image_index')
        
        # Load knowledge bases if not already loaded
        if self.rag.text_vector_store is None:
            self.rag.load_text_knowledge_base(self.text_kb_path)
        if self.rag.image_vector_store is None:
            self.rag.load_image_knowledge_base(self.image_kb_path)
        
        # Save vector stores
        self.rag.text_vector_store.save_local(text_index_path)
        self.rag.image_vector_store.save_local(image_index_path)
        
        # Create new RAG instance and load saved indices
        new_rag = DeepSeekImageRAG(
            model_name="deepseek-ai/deepseek-coder-1.3b-base",
            embedding_model="BAAI/bge-large-en-v1.5",
            image_embedding_model="openai/clip-vit-base-patch32"
        )
        
        # Load saved indices
        new_rag.load_index(text_index_path, image_index_path)
        
        # Verify loaded vector stores work
        query = "red"
        results = new_rag.search(query)
        self.assertTrue(len(results["texts"]) > 0)
        self.assertTrue(len(results["images"]) > 0)

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    unittest.main(verbosity=2) 

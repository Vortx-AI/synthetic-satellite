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
import requests
from io import BytesIO

# Load environment variables
load_dotenv()

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
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
        
        # Download and create test images
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
    def download_image(cls, url: str, filename: str) -> str:
        """Download image from URL and save to test directory"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            path = os.path.join(cls.test_data_dir, filename)
            img.save(path)
            return path
        except Exception as e:
            print(f"Failed to download image {url}: {str(e)}")
            # Create a fallback colored image
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            path = os.path.join(cls.test_data_dir, filename)
            img.save(path)
            return path
    
    @classmethod
    def create_test_images(cls):
        """Create and download test images"""
        # Dictionary of image URLs and their descriptions
        image_data = {
            'golden_gate.jpg': {
                'url': 'https://images.unsplash.com/photo-1501594907352-04cda38ebc29',
                'description': 'Golden Gate Bridge in San Francisco',
                'fallback_color': (218, 165, 32)  # Golden color
            },
            'alcatraz.jpg': {
                'url': 'https://images.unsplash.com/photo-1549415697-8d2a5a2e1c68',
                'description': 'Alcatraz Island prison',
                'fallback_color': (128, 128, 128)  # Gray color
            },
            'pier39.jpg': {
                'url': 'https://images.unsplash.com/photo-1569959220744-ff553533f492',
                'description': 'Pier 39 in San Francisco',
                'fallback_color': (70, 130, 180)  # Steel blue
            }
        }
        
        cls.image_paths = {}
        for filename, data in image_data.items():
            try:
                # Try to download the image
                path = cls.download_image(data['url'], filename)
            except Exception:
                # If download fails, create a colored image
                img = Image.new('RGB', (100, 100), data['fallback_color'])
                path = os.path.join(cls.test_data_dir, filename)
                img.save(path)
            cls.image_paths[filename] = path
    
    @classmethod
    def create_test_knowledge_bases(cls):
        """Create test knowledge base files with San Francisco landmarks"""
        # Create text knowledge base
        cls.text_kb_path = os.path.join(cls.test_data_dir, 'text_kb.json')
        text_kb = {
            "documents": [
                {
                    "content": "The Golden Gate Bridge is an iconic suspension bridge spanning the Golden Gate strait. "
                              "It connects San Francisco to Marin County and is known for its distinctive orange color "
                              "and art deco design. The bridge spans 1.7 miles and stands as one of the most photographed "
                              "landmarks in the world.",
                    "metadata": {"type": "landmark", "subject": "Golden Gate Bridge"}
                },
                {
                    "content": "Alcatraz Island, located in San Francisco Bay, was once a maximum security federal prison. "
                              "Known as 'The Rock', it housed notorious criminals like Al Capone. Today, it's a popular "
                              "tourist destination managed by the National Park Service, offering visitors a glimpse into "
                              "its fascinating history.",
                    "metadata": {"type": "landmark", "subject": "Alcatraz"}
                },
                {
                    "content": "Pier 39 is a popular shopping center and tourist attraction built on a pier in San Francisco. "
                              "It's famous for its resident sea lions, numerous shops and restaurants, and views of "
                              "Alcatraz Island and the Golden Gate Bridge. The pier is also home to street performers "
                              "and various entertainment options.",
                    "metadata": {"type": "landmark", "subject": "Pier 39"}
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
                    "path": cls.image_paths['golden_gate.jpg'],
                    "metadata": {
                        "type": "landmark",
                        "subject": "Golden Gate Bridge",
                        "description": "Iconic orange suspension bridge in San Francisco"
                    }
                },
                {
                    "path": cls.image_paths['alcatraz.jpg'],
                    "metadata": {
                        "type": "landmark",
                        "subject": "Alcatraz",
                        "description": "Historic prison island in San Francisco Bay"
                    }
                },
                {
                    "path": cls.image_paths['pier39.jpg'],
                    "metadata": {
                        "type": "landmark",
                        "subject": "Pier 39",
                        "description": "Popular tourist destination with shops and sea lions"
                    }
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
        # Load knowledge bases if not already loaded
        if self.rag.text_vector_store is None:
            self.rag.load_text_knowledge_base(self.text_kb_path)
        if self.rag.image_vector_store is None:
            self.rag.load_image_knowledge_base(self.image_kb_path)
        
        # Test search with different queries
        queries = [
            "Golden Gate Bridge",
            "Alcatraz prison",
            "tourist attractions in San Francisco"
        ]
        
        for query in queries:
            results = self.rag.search(query)
            
            # Verify results structure
            self.assertIn("texts", results)
            self.assertIn("images", results)
            
            # Verify we got some results
            self.assertTrue(len(results["texts"]) > 0)
            self.assertTrue(len(results["images"]) > 0)
    
    def test_generate_answer(self):
        """Test answer generation"""
        # Load knowledge bases if not already loaded
        if self.rag.text_vector_store is None:
            self.rag.load_text_knowledge_base(self.text_kb_path)
        if self.rag.image_vector_store is None:
            self.rag.load_image_knowledge_base(self.image_kb_path)
        
        # Test generation with different queries
        queries = [
            "What can you tell me about the Golden Gate Bridge?",
            "Describe Alcatraz Island and its history.",
            "What attractions can I find at Pier 39?"
        ]
        
        for query in queries:
            answer = self.rag.generate_answer(query)
            
            # Verify we got a non-empty answer
            self.assertIsNotNone(answer)
            self.assertTrue(len(answer) > 0)
            
            # Verify answer contains relevant information
            self.assertTrue(any(keyword in answer.lower() 
                              for keyword in query.lower().split()))
    
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
        
        # Test search with the new instance
        queries = ["Golden Gate Bridge", "Alcatraz", "Pier 39"]
        for query in queries:
            results = new_rag.search(query)
            self.assertTrue(len(results["texts"]) > 0)
            self.assertTrue(len(results["images"]) > 0)

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    unittest.main(verbosity=2) 
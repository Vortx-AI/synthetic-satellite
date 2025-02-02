from vllm import LLM, SamplingParams
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Dict, Optional
import json
import torch
import logging
from pathlib import Path

class DeepSeekRAG:
    def __init__(
        self,
        model_name: str = "deepseek-ai/deepseek-coder-33b-instruct",
        embedding_model: str = "BAAI/bge-large-en-v1.5",
        index_path: Optional[str] = None,
        knowledge_base_path: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_k_docs: int = 3,
        verbose: bool = False
    ):
        """
        Initialize DeepSeek RAG system
        
        Args:
            model_name: DeepSeek model name/path
            embedding_model: Sentence transformer model for embeddings
            index_path: Path to save/load FAISS index
            knowledge_base_path: Path to knowledge base documents
            max_tokens: Maximum tokens for generation
            temperature: Sampling temperature
            top_k_docs: Number of documents to retrieve
            verbose: Enable verbose logging
        """
        self.setup_logging(verbose)
        self.top_k = top_k_docs
        
        # Initialize LLM with float16 dtype
        self.logger.info("Initializing DeepSeek LLM...")
        self.model = LLM(
            model=model_name,
            trust_remote_code=True,
            max_model_len=max_tokens,
            dtype="float16"  # Explicitly set to float16 for T4 GPU compatibility
        )
        
        # Initialize embedding model
        self.logger.info("Initializing embedding model...")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Setup FAISS index
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Load or create knowledge base
        self.documents = []
        if index_path and Path(index_path).exists():
            self.load_index(index_path)
        elif knowledge_base_path:
            self.load_knowledge_base(knowledge_base_path)
        
        # Set sampling parameters
        self.sampling_params = SamplingParams(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.95,
            presence_penalty=0.1
        )
    
    def setup_logging(self, verbose: bool):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO if verbose else logging.WARNING,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_knowledge_base(self, path: str):
        """Load documents from knowledge base"""
        self.logger.info(f"Loading knowledge base from {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            # Add documents to index
            self.add_documents(documents)
            self.logger.info(f"Loaded {len(documents)} documents")
            
        except Exception as e:
            self.logger.error(f"Error loading knowledge base: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, str]]):
        """Add documents to the index"""
        try:
            # Get embeddings for documents
            texts = [doc['content'] for doc in documents]
            embeddings = self.embedding_model.encode(texts)
            
            # Add to FAISS index
            self.index.add(np.array(embeddings).astype('float32'))
            
            # Store documents
            self.documents.extend(documents)
            
        except Exception as e:
            self.logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def save_index(self, path: str):
        """Save FAISS index and documents"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, f"{path}.index")
            
            # Save documents
            with open(f"{path}.json", 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2)
                
            self.logger.info(f"Saved index and documents to {path}")
            
        except Exception as e:
            self.logger.error(f"Error saving index: {str(e)}")
            raise
    
    def load_index(self, path: str):
        """Load FAISS index and documents"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{path}.index")
            
            # Load documents
            with open(f"{path}.json", 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
                
            self.logger.info(f"Loaded index with {len(self.documents)} documents")
            
        except Exception as e:
            self.logger.error(f"Error loading index: {str(e)}")
            raise
    
    def retrieve(self, query: str) -> List[str]:
        """Retrieve relevant documents for query"""
        try:
            # Get query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search in FAISS
            distances, indices = self.index.search(
                np.array(query_embedding).astype('float32'), 
                self.top_k
            )
            
            # Get relevant documents
            retrieved_docs = [self.documents[i]['content'] for i in indices[0]]
            return retrieved_docs
            
        except Exception as e:
            self.logger.error(f"Error during retrieval: {str(e)}")
            raise
    
    def generate(self, query: str) -> str:
        """Generate response using RAG"""
        try:
            # Retrieve relevant documents
            retrieved_docs = self.retrieve(query)
            
            # Create prompt with context
            context = "\n".join(retrieved_docs)
            prompt = f"""Context information:
{context}

Based on the above context, please answer the following question:
{query}

Answer:"""
            
            # Generate response
            outputs = self.model.generate([prompt], self.sampling_params)
            response = outputs[0].outputs[0].text.strip()
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error during generation: {str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    # Initialize RAG system
    rag = DeepSeekRAG(
        knowledge_base_path="./knowledge_base.json",
        verbose=True
    )
    
    # Example knowledge base documents
    documents = [
        {
            "content": "Python is a high-level programming language known for its simplicity and readability.",
            "metadata": {"source": "doc1", "type": "programming"}
        },
        {
            "content": "FAISS is a library for efficient similarity search developed by Facebook Research.",
            "metadata": {"source": "doc2", "type": "technology"}
        }
    ]
    
    # Add documents
    rag.add_documents(documents)
    
    # Save index
    rag.save_index("data/rag_index")
    
    # Test query
    query = "What is Python programming language?"
    response = rag.generate(query)
    print(f"\nQuery: {query}")
    print(f"Response: {response}") 
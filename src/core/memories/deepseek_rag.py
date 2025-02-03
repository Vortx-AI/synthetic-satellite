from vllm import LLM, SamplingParams
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List, Dict, Optional
import json
import torch
import logging
from pathlib import Path
import gc
import os

# Set PyTorch memory management environment variables
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'

class DeepSeekRAG:
    def __init__(
        self,
        model_name: str = "deepseek-ai/deepseek-coder-1.3b-base",
        embedding_model: str = "BAAI/bge-large-en-v1.5",
        index_path: Optional[str] = None,
        knowledge_base_path: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_k_docs: int = 3,
        verbose: bool = False
    ):
        """
        Initialize DeepSeek RAG system with LangChain
        
        Args:
            model_name: DeepSeek model name/path
            embedding_model: Model for embeddings
            index_path: Path to save/load FAISS index
            knowledge_base_path: Path to knowledge base documents
            max_tokens: Maximum tokens for generation
            temperature: Sampling temperature
            top_k_docs: Number of documents to retrieve
            verbose: Enable verbose logging
        """
        self.setup_logging(verbose)
        self.top_k = top_k_docs
        
        # Initialize LLM
        self.logger.info("Initializing DeepSeek LLM...")
        self.model = LLM(
            model=model_name,
            trust_remote_code=True,
            tensor_parallel_size=1,
            dtype="float16",
            max_model_len=512,
            gpu_memory_utilization=0.6,
            enforce_eager=True
        )
        
        # Set sampling parameters
        self.sampling_params = SamplingParams(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.95,
            presence_penalty=0.1
        )
        
        # Initialize embedding model using LangChain
        self.logger.info("Initializing embedding model...")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cuda'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize or load vector store
        if index_path and Path(index_path).exists():
            self.load_index(index_path)
        else:
            self.vector_store = None
            if knowledge_base_path:
                self.load_knowledge_base(knowledge_base_path)
        
        # Setup RAG prompt template
        self.rag_prompt = PromptTemplate(
            template="""Context information:
{context}

Based on the above context, please answer the following question:
{query}

Answer:""",
            input_variables=["context", "query"]
        )
        
    def setup_logging(self, verbose: bool):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO if verbose else logging.WARNING,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def _cleanup(self):
        """Clean up GPU memory"""
        try:
            gc.collect()
            if torch.cuda.is_available():
                with torch.cuda.device('cuda'):
                    torch.cuda.empty_cache()
                    torch.cuda.ipc_collect()
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {str(e)}")
    
    def load_knowledge_base(self, path: str):
        """Load documents from knowledge base"""
        self.logger.info(f"Loading knowledge base from {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            # Create vector store
            texts = [doc['content'] for doc in documents]
            metadatas = [{'source': doc.get('metadata', {})} for doc in documents]
            
            self.vector_store = FAISS.from_texts(
                texts=texts,
                embedding=self.embedding_model,
                metadatas=metadatas
            )
            
            self.logger.info(f"Loaded {len(documents)} documents")
            
        except Exception as e:
            self.logger.error(f"Error loading knowledge base: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, str]]):
        """Add documents to the vector store"""
        try:
            texts = [doc['content'] for doc in documents]
            metadatas = [{'source': doc.get('metadata', {})} for doc in documents]
            
            if self.vector_store is None:
                self.vector_store = FAISS.from_texts(
                    texts=texts,
                    embedding=self.embedding_model,
                    metadatas=metadatas
                )
            else:
                self.vector_store.add_texts(texts=texts, metadatas=metadatas)
            
        except Exception as e:
            self.logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def save_index(self, path: str):
        """Save vector store"""
        try:
            if self.vector_store:
                self.vector_store.save_local(path)
                self.logger.info(f"Saved vector store to {path}")
            
        except Exception as e:
            self.logger.error(f"Error saving index: {str(e)}")
            raise
    
    def load_index(self, path: str):
        """Load vector store"""
        try:
            self.vector_store = FAISS.load_local(
                folder_path=path,
                embeddings=self.embedding_model
            )
            self.logger.info(f"Loaded vector store from {path}")
            
        except Exception as e:
            self.logger.error(f"Error loading index: {str(e)}")
            raise
    
    def retrieve(self, query: str) -> List[str]:
        """Retrieve relevant documents for query"""
        try:
            if not self.vector_store:
                raise ValueError("No documents in vector store")
            
            # Search in vector store
            docs = self.vector_store.similarity_search(query, k=self.top_k)
            
            # Get document contents
            retrieved_docs = [doc.page_content for doc in docs]
            return retrieved_docs
            
        except Exception as e:
            self.logger.error(f"Error during retrieval: {str(e)}")
            raise
    
    def generate(self, query: str) -> str:
        """Generate response using RAG"""
        try:
            self._cleanup()  # Clean up before generation
            
            # Retrieve relevant documents
            retrieved_docs = self.retrieve(query)
            
            # Format prompt with context
            context = "\n".join(retrieved_docs)
            formatted_prompt = self.rag_prompt.format(
                context=context,
                query=query
            )
            
            # Generate response using vLLM
            outputs = self.model.generate(formatted_prompt, self.sampling_params)
            response = outputs[0].outputs[0].text.strip()
            
            self._cleanup()  # Clean up after generation
            return response
            
        except Exception as e:
            self.logger.error(f"Error during generation: {str(e)}")
            self._cleanup()  # Clean up on error
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
    
    try:
        # Add documents
        rag.add_documents(documents)
        
        # Save index
        rag.save_index("data/rag_index")
        
        # Test query
        query = "What is Python programming language?"
        response = rag.generate(query)
        print(f"\nQuery: {query}")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

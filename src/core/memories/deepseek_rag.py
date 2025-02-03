from vllm import LLM, SamplingParams
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List, Dict, Optional
import json
import torch
import logging
from pathlib import Path
import gc
import os

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
        """
        self.setup_logging(verbose)
        self.top_k = top_k_docs
        
        # Initialize vector store
        self.vector_store = None
        
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
        elif knowledge_base_path:
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
    
    def load_knowledge_base(self, path: str):
        """Load documents from knowledge base"""
        self.logger.info(f"Loading knowledge base from {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different possible JSON formats
            if isinstance(data, list):
                documents = data
            elif isinstance(data, dict) and 'documents' in data:
                documents = data['documents']
            elif isinstance(data, str):
                # Handle single document as string
                documents = [{"content": data, "metadata": {}}]
            else:
                raise ValueError(f"Unsupported knowledge base format in {path}")
            
            # Validate and normalize documents
            normalized_docs = []
            for doc in documents:
                if isinstance(doc, str):
                    # Convert string documents to proper format
                    normalized_docs.append({
                        "content": doc,
                        "metadata": {}
                    })
                elif isinstance(doc, dict) and 'content' in doc:
                    # Use existing document structure
                    normalized_docs.append(doc)
                else:
                    self.logger.warning(f"Skipping invalid document format: {doc}")
                    continue
            
            if not normalized_docs:
                raise ValueError("No valid documents found in knowledge base")
            
            # Add normalized documents
            self.add_documents(normalized_docs)
            self.logger.info(f"Loaded {len(normalized_docs)} documents")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format in knowledge base: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading knowledge base: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, str]]):
        """Add documents to the vector store"""
        try:
            # Validate and extract document content
            texts = []
            metadatas = []
            
            for doc in documents:
                if isinstance(doc, dict) and 'content' in doc:
                    texts.append(doc['content'])
                    metadatas.append({
                        'source': doc.get('metadata', {}).get('source', 'unknown'),
                        'type': doc.get('metadata', {}).get('type', 'unknown')
                    })
                else:
                    self.logger.warning(f"Skipping invalid document format: {doc}")
                    continue
            
            if not texts:
                raise ValueError("No valid documents to add")
            
            # Create or update vector store
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
                # Create directory if it doesn't exist
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                self.vector_store.save_local(path)
                self.logger.info(f"Saved vector store to {path}")
            else:
                self.logger.warning("No vector store to save")
            
        except Exception as e:
            self.logger.error(f"Error saving index: {str(e)}")
            raise
    
    def load_index(self, path: str):
        """Load vector store"""
        try:
            if not Path(path).exists():
                raise FileNotFoundError(f"Index path {path} does not exist")
            
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
            
            # Use similarity_search instead of direct embedding
            docs = self.vector_store.similarity_search(
                query,
                k=self.top_k
            )
            
            # Extract document contents
            retrieved_docs = [doc.page_content for doc in docs]
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


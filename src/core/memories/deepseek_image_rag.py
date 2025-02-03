from vllm import LLM, SamplingParams
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List, Dict, Optional, Any
import json
import torch
import logging
from pathlib import Path
import os
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from dataclasses import dataclass

@dataclass
class SyntheticConfig:
    image_embedding_model: str = "openai/clip-vit-base-patch32"
    # Add other configuration parameters if needed

class DeepSeekImageRAG:
    def __init__(
        self,
        model_name: str = "deepseek-ai/deepseek-coder-1.3b-base",
        embedding_model: str = "BAAI/bge-large-en-v1.5",
        image_embedding_model: str = "openai/clip-vit-base-patch32",
        index_path: Optional[str] = None,
        image_index_path: Optional[str] = None,
        knowledge_base_path: Optional[str] = None,
        image_knowledge_base_path: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_k_docs: int = 3,
        verbose: bool = False
    ):
        """
        Initialize DeepSeek Image RAG system with LangChain and Image RAG capabilities
        """
        self.setup_logging(verbose)
        self.top_k = top_k_docs
        
        # Initialize text vector store
        self.text_vector_store = None
        
        # Initialize image vector store
        self.image_vector_store = None
        
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
        
        # Initialize text embedding model using LangChain
        self.logger.info("Initializing text embedding model...")
        self.text_embedding_model = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cuda'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize image embedding model using CLIP
        self.logger.info("Initializing image embedding model...")
        self.clip_model = CLIPModel.from_pretrained(image_embedding_model)
        self.clip_processor = CLIPProcessor.from_pretrained(image_embedding_model)
        
        # Initialize or load text vector store
        if index_path and Path(index_path).exists():
            self.load_text_index(index_path)
        elif knowledge_base_path:
            self.load_text_knowledge_base(knowledge_base_path)
        
        # Initialize or load image vector store
        if image_index_path and Path(image_index_path).exists():
            self.load_image_index(image_index_path)
        elif image_knowledge_base_path:
            self.load_image_knowledge_base(image_knowledge_base_path)
        
        # Setup RAG prompt template
        self.rag_prompt = PromptTemplate(
            template="""Context information:
    {text_context}
    {image_context}
    
    Based on the above context, please answer the following question:
    {query}
    
    Answer:""",
            input_variables=["text_context", "image_context", "query"]
        )
    
    def setup_logging(self, verbose: bool):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO if verbose else logging.WARNING,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_text_index(self, index_path: str):
        """Load existing text vector store index"""
        self.text_vector_store = FAISS.load_local(index_path, self.text_embedding_model)
        self.logger.info(f"Loaded text vector store from {index_path}")
    
    def load_image_index(self, image_index_path: str):
        """Load existing image vector store index"""
        # Assuming image embeddings are stored separately
        self.image_vector_store = FAISS.load_local(image_index_path, self.get_image_embeddings)
        self.logger.info(f"Loaded image vector store from {image_index_path}")
    
    def load_text_knowledge_base(self, path: str):
        """Load textual documents from knowledge base"""
        self.logger.info(f"Loading textual knowledge base from {path}")
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
            self.add_text_documents(normalized_docs)
            self.logger.info(f"Loaded {len(normalized_docs)} textual documents")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format in knowledge base: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading textual knowledge base: {str(e)}")
            raise
    
    def load_image_knowledge_base(self, path: str):
        """Load images from knowledge base"""
        self.logger.info(f"Loading image knowledge base from {path}")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different possible JSON formats
            if isinstance(data, list):
                images = data
            elif isinstance(data, dict) and 'images' in data:
                images = data['images']
            elif isinstance(data, str):
                # Handle single image as string path
                images = [{"path": data, "metadata": {}}]
            else:
                raise ValueError(f"Unsupported image knowledge base format in {path}")
            
            # Validate and normalize images
            normalized_images = []
            for img in images:
                if isinstance(img, str):
                    # Convert string paths to proper format
                    normalized_images.append({
                        "path": img,
                        "metadata": {}
                    })
                elif isinstance(img, dict) and 'path' in img:
                    # Use existing image structure
                    normalized_images.append(img)
                else:
                    self.logger.warning(f"Skipping invalid image format: {img}")
                    continue
            
            if not normalized_images:
                raise ValueError("No valid images found in knowledge base")
            
            # Add normalized images
            self.add_images(normalized_images)
            self.logger.info(f"Loaded {len(normalized_images)} images")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format in image knowledge base: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading image knowledge base: {str(e)}")
            raise
    
    def add_text_documents(self, documents: List[Dict[str, str]]):
        """Add textual documents to the text vector store"""
        try:
            texts = [doc['content'] for doc in documents]
            embeddings = self.text_embedding_model.embed_documents(texts)
            self.text_vector_store.add_texts(
                texts,
                embeddings,
                metadatas=[doc.get('metadata', {}) for doc in documents]
            )
            self.logger.info(f"Added {len(texts)} textual documents to the vector store")
        except Exception as e:
            self.logger.error(f"Error adding textual documents: {str(e)}")
            raise
    
    def add_images(self, images: List[Dict[str, Any]]):
        """Add images to the image vector store"""
        try:
            image_embeddings = []
            metadata_list = []
            for img in images:
                img_path = img['path']
                if not Path(img_path).exists():
                    self.logger.warning(f"Image path does not exist: {img_path}")
                    continue
                image = Image.open(img_path).convert("RGB")
                inputs = self.clip_processor(images=image, return_tensors="pt")
                with torch.no_grad():
                    image_features = self.clip_model.get_image_features(**inputs)
                embedding = image_features.squeeze().numpy()
                image_embeddings.append(embedding)
                metadata_list.append(img.get('metadata', {'path': img_path}))
            
            if image_embeddings:
                self.image_vector_store = FAISS.from_embeddings(
                    image_embeddings,
                    metadatas=metadata_list
                )
                self.logger.info(f"Added {len(image_embeddings)} images to the image vector store")
            else:
                self.logger.warning("No valid images were added to the image vector store")
        except Exception as e:
            self.logger.error(f"Error adding images: {str(e)}")
            raise
    
    def search(self, query: str, include_images: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """Search for relevant textual documents and images based on the query"""
        text_results = self.text_vector_store.similarity_search(query, self.top_k) if self.text_vector_store else []
        result = {"texts": text_results}
        
        if include_images and self.image_vector_store:
            image_results = self.image_vector_store.similarity_search(query, self.top_k)
            result["images"] = image_results
        return result
    
    def generate_answer(self, query: str) -> str:
        """Generate an answer based on retrieved textual and image contexts"""
        results = self.search(query)
        text_context = "\n".join([doc['document'] for doc in results.get("texts", [])])
        
        # Prepare image context using Markdown image syntax
        image_context = ""
        for img in results.get("images", []):
            image_path = img['metadata'].get('path', '')
            if image_path:
                # Convert local image path to a URL or embed as needed
                # Here, we'll assume images are served locally or accessible via a URL
                image_url = f"file://{image_path}"  # Modify as per your setup
                image_context += f"![Image]({image_url})\n"
        
        # Fill in the prompt
        prompt = self.rag_prompt.format(
            text_context=text_context,
            image_context=image_context,
            query=query
        )
        
        # Generate the answer using the LLM
        response = self.model.generate(
            prompt,
            self.sampling_params
        )
        answer = response.text.strip()
        return answer 
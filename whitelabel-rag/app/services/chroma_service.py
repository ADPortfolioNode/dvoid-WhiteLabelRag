"""
ChromaDB service for vector storage and retrieval
"""

import os
import logging
import chromadb
from chromadb.utils import embedding_functions
import google.generativeai as genai
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ChromaService:
    """Service for managing ChromaDB operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._setup_chroma()
    
    def _setup_chroma(self):
        """Setup ChromaDB client and collections."""
        try:
            # Get configuration
            chroma_path = os.environ.get('CHROMA_DB_PATH', './chromadb_data')
            
            # Ensure directory exists
            os.makedirs(chroma_path, exist_ok=True)
            
            # Initialize ChromaDB client with proper configuration
            self.client = chromadb.PersistentClient(
                path=chroma_path
            )
            logger.info(f"ChromaDB PersistentClient initialized at {chroma_path}")
            
            # Setup embedding function
            self._setup_embedding_function()
            
            # Get or create collections
            self.documents_collection = self.client.get_or_create_collection(
                name="documents",
                embedding_function=self.embedding_function,
                metadata={"description": "Document chunks for RAG"}
            )
            
            self.steps_collection = self.client.get_or_create_collection(
                name="steps",
                embedding_function=self.embedding_function,
                metadata={"description": "Task step embeddings"}
            )
            
            logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up ChromaDB: {str(e)}")
            raise
    
    def _setup_embedding_function(self):
        """Setup embedding function for ChromaDB."""
        try:
            # Use Google Generative AI embedding function
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.embedding_function = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                    api_key=api_key,
                    model_name="models/embedding-001"
                )
                logger.info("✅ Google Generative AI embedding function configured")
            else:
                # Fallback to sentence transformers
                logger.warning("⚠️ GEMINI_API_KEY not found, falling back to SentenceTransformer embeddings")
                self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="all-MiniLM-L6-v2"
                )
                logger.info("✅ SentenceTransformer embedding function configured")
            
        except Exception as e:
            logger.error(f"Error setting up embedding function: {str(e)}")
            logger.warning("⚠️ Falling back to default embedding function")
            # Fallback to default
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
    
    def store_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store a document chunk in the vector database."""
        try:
            # Generate unique ID
            doc_id = f"doc_{len(self.documents_collection.get()['ids'])}"
            
            # Store in collection
            self.documents_collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Stored document chunk with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error storing document: {str(e)}")
            raise
    
    def store_step_embedding(self, step_id: str, content: str, metadata: Dict[str, Any]) -> str:
        """Store a step embedding in the vector database."""
        try:
            self.steps_collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[step_id]
            )
            
            logger.info(f"Stored step embedding with ID: {step_id}")
            return step_id
            
        except Exception as e:
            logger.error(f"Error storing step embedding: {str(e)}")
            raise
    
    def query_documents(self, query: str, n_results: int = 3, 
                       where: Optional[Dict] = None) -> Dict[str, Any]:
        """Query documents using vector similarity search."""
        try:
            results = self.documents_collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            logger.info(f"Query returned {len(results['documents'][0])} results")
            return results
            
        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}")
            return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
    
    def query_steps(self, query: str, n_results: int = 3) -> Dict[str, Any]:
        """Query step embeddings using vector similarity search."""
        try:
            results = self.steps_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying steps: {str(e)}")
            return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collections."""
        try:
            doc_count = self.documents_collection.count()
            step_count = self.steps_collection.count()
            
            return {
                'documents_count': doc_count,
                'steps_count': step_count,
                'total_items': doc_count + step_count
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {'documents_count': 0, 'steps_count': 0, 'total_items': 0}
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the collection."""
        try:
            self.documents_collection.delete(ids=[doc_id])
            logger.info(f"Deleted document with ID: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
    
    def reset_collections(self):
        """Reset all collections (use with caution)."""
        try:
            self.client.delete_collection("documents")
            self.client.delete_collection("steps")
            
            # Recreate collections
            self.documents_collection = self.client.get_or_create_collection(
                name="documents",
                embedding_function=self.embedding_function
            )
            
            self.steps_collection = self.client.get_or_create_collection(
                name="steps",
                embedding_function=self.embedding_function
            )
            
            logger.info("Collections reset successfully")
            
        except Exception as e:
            logger.error(f"Error resetting collections: {str(e)}")
            raise

# Singleton instance
_chroma_service_instance = None

def get_chroma_service_instance() -> ChromaService:
    """Get the singleton ChromaService instance."""
    global _chroma_service_instance
    if _chroma_service_instance is None:
        _chroma_service_instance = ChromaService()
    return _chroma_service_instance
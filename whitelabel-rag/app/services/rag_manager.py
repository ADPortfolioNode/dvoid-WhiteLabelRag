"""
RAG Manager for orchestrating retrieval-augmented generation workflows
"""

import logging
from typing import List, Dict, Any
from app.services.chroma_service import get_chroma_service_instance
import os
import importlib

logger = logging.getLogger(__name__)

class RAGManager:
    """Manager for RAG workflows and document processing."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGManager, cls).__new__(cls)
            cls._instance.chroma_service = None
            cls._instance.llm = None
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.initialized = True
            self.chroma_service = get_chroma_service_instance()
            # Dynamically load all services in app/services/
            self.services = {}
            services_dir = os.path.dirname(__file__)
            for fname in os.listdir(services_dir):
                if fname.endswith(".py") and fname not in ("__init__.py", "rag_manager.py"):
                    mod_name = f"app.services.{fname[:-3]}"
                    try:
                        mod = importlib.import_module(mod_name)
                        self.services[fname[:-3]] = mod
                    except Exception:
                        pass
            # Google Search Service
            try:
                from app.services.google_search_service import GoogleSearchService
                self.google_search = GoogleSearchService()
            except Exception:
                self.google_search = None
            # SBA Service integration
            try:
                from app.services.sba_service import SBAService
                self.sba_service = SBAService()
            except Exception:
                self.sba_service = None
    
    def store_document_chunk(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store a document chunk in the vector database."""
        return self.chroma_service.store_document(content, metadata)
    
    def query_documents(self, query, n_results=3):
        # Basic RAG: Query → Retrieve → Generate
        results = self.chroma_service.query(query, top_k=n_results)
        return {"results": results}

    # Advanced, Recursive, and Adaptive RAG workflows can be added here as methods
    def advanced_rag_workflow(self, query):
        # Example: expand query, multi-strategy retrieval, rerank, etc.
        # ...implement as per INSTRUCTIONS.md...
        pass

    def recursive_rag_workflow(self, query):
        # Example: initial retrieval, plan, targeted retrieval, etc.
        # ...implement as per INSTRUCTIONS.md...
        pass

    def adaptive_rag_workflow(self, query):
        # Example: analyze query, select workflow, evaluate/refine
        # ...implement as per INSTRUCTIONS.md...
        pass

    def get_collection_stats(self):
        return self.chroma_service.get_collection_stats()
    
    @classmethod
    def _reset_instance(cls):
        """Reset the singleton instance (for testing/mocking)."""
        cls._instance = None

# Singleton instance
_rag_manager_instance = None

def get_rag_manager() -> RAGManager:
    """Get the singleton RAGManager instance, or a new one in test mode."""
    if os.environ.get('TEST_MODE') == '1' or 'pytest' in sys.modules:
        return RAGManager()
    global _rag_manager_instance
    if _rag_manager_instance is None:
        _rag_manager_instance = RAGManager()
    return _rag_manager_instance

def get_sba_service_instance():
    """Stub for SBA service instance for testing/mocking purposes."""
    return None
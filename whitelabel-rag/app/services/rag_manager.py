"""
RAG Manager for orchestrating retrieval-augmented generation workflows
"""

import logging
from typing import List, Dict, Any, Optional
from app.services.chroma_service import get_chroma_service_instance
from app.services.llm_factory import LLMFactory
from app.services.internet_search_agent import get_internet_search_agent_instance

logger = logging.getLogger(__name__)

class RAGManager:
    """Manager for RAG workflows and document processing."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.chroma_service = None
            self.llm = LLMFactory.get_llm()
            self.internet_search_agent = None

    def initialize_services(self):
        self.chroma_service = get_chroma_service_instance()
        self.internet_search_agent = get_internet_search_agent_instance()

    def store_document_chunk(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store a document chunk in the vector database."""
        return self.chroma_service.store_document(content, metadata)
    
    def query_documents(self, query: str, n_results: int = 3, 
                       workflow_type: str = "basic", force_internet_search: bool = False) -> Dict[str, Any]:
        """Query documents using specified RAG workflow."""
        
        self.initialize_services() # Ensures chroma_service and internet_search_agent are attempted to be initialized
        
        if workflow_type == "basic":
            rag_response = self._basic_rag_workflow(query, n_results)
        elif workflow_type == "advanced":
            rag_response = self._advanced_rag_workflow(query, n_results)
        elif workflow_type == "recursive":
            rag_response = self._recursive_rag_workflow(query, n_results)
        elif workflow_type == "adaptive":
            rag_response = self._adaptive_rag_workflow(query, n_results)
        else:
            rag_response = self._basic_rag_workflow(query, n_results) # Default to basic
        
        # Determine if internet search fallback is needed
        need_internet_search = force_internet_search
        
        if not force_internet_search: # Only evaluate if not already forced
            if rag_response.get('error'):
                need_internet_search = True
            # Check if RAG response indicates no useful local results
            elif not rag_response.get('context_used', False) and not rag_response.get('sources'):
                need_internet_search = True
            elif rag_response.get('text', '').strip().startswith("I couldn't find any relevant documents") or \
                 rag_response.get('text', '').strip().startswith("Error processing query"):
                need_internet_search = True
        
        internet_search_response = None
        if need_internet_search:
            if self.internet_search_agent:
                logger.info(f"Performing internet search for query: {query}")
                internet_search_response = self.internet_search_agent.search(query, num_results=n_results)
            else:
                logger.warning("Internet search agent not initialized. Skipping internet search.")
                internet_search_response = {"error": "Internet search agent not available.", "text": "", "sources": [], "results": []}
        
        return {
            'rag_response': rag_response,
            'internet_search_response': internet_search_response
        }
    
    def _basic_rag_workflow(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Single-Stage RAG (Basic)
        Workflow: Query -> Retrieve -> Generate
        """
        try:
            logger.info(f"Executing basic RAG workflow for query: {query}")
            
            # Retrieve relevant documents
            retrieved_docs = self.chroma_service.query_documents(query, top_k)
            
            if not retrieved_docs['documents'][0]:
                return {
                    'text': "I couldn't find any relevant documents to answer your question.",
                    'sources': [],
                    'workflow': 'basic',
                    'results': []
                }
            
            # Format context from retrieved documents
            documents = retrieved_docs['documents'][0]
            metadatas = retrieved_docs['metadatas'][0]
            distances = retrieved_docs['distances'][0]
            
            context = "\n\n".join(documents)
            sources = [meta.get('source', 'Unknown') for meta in metadatas]
            
            # Generate response using LLM with context
            system_prompt = """
            You are a helpful assistant that answers questions based on the provided context.
            Use only the information from the context to answer the question.
            If the context doesn't contain enough information, say so clearly.
            Always cite your sources when possible.
            """
            
            response_text = LLMFactory.generate_response(
                prompt=f"Context:\n{context}\n\nQuestion: {query}",
                system_prompt=system_prompt,
                temperature=0.2
            )
            
            # Format results for return
            results = []
            for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
                results.append({
                    'content': doc,
                    'metadata': meta,
                    'distance': dist,
                    'rank': i + 1
                })
            
            return {
                'text': response_text,
                'sources': list(set(sources)),  # Remove duplicates
                'workflow': 'basic',
                'results': results,
                'context_used': True
            }
            
        except Exception as e:
            logger.error(f"Error in basic RAG workflow: {str(e)}")
            return {
                'text': f"Error processing query: {str(e)}",
                'sources': [],
                'workflow': 'basic',
                'results': [],
                'error': True
            }
    
    def _advanced_rag_workflow(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Multi-Stage RAG (Advanced)
        Workflow: Query → Query Processing → Retrieval → Filtering → Generation → Post-processing
        """
        try:
            logger.info(f"Executing advanced RAG workflow for query: {query}")
            
            # Query processing - expand query for better recall
            expanded_query = self._expand_query(query)
            
            # Multi-strategy retrieval
            semantic_results = self.chroma_service.query_documents(expanded_query, top_k)
            keyword_results = self.chroma_service.query_documents(query, top_k)
            
            # Merge and rerank results
            merged_results = self._merge_search_results(semantic_results, keyword_results)
            reranked_results = self._rerank_results(merged_results, query)
            
            # Take top results after reranking
            top_results = reranked_results[:3]
            
            if not top_results:
                return {
                    'text': "I couldn't find any relevant documents to answer your question.",
                    'sources': [],
                    'workflow': 'advanced',
                    'results': []
                }
            
            # Format context from top results
            context = "\n\n".join([result['content'] for result in top_results])
            sources = [result['metadata'].get('source', 'Unknown') for result in top_results]
            
            # Generate response
            system_prompt = """
            You are an expert assistant that provides comprehensive answers based on provided context.
            Analyze the context carefully and provide a detailed, well-structured response.
            Include relevant details and cite sources when appropriate.
            """
            
            response_text = LLMFactory.generate_response(
                prompt=f"Context:\n{context}\n\nQuestion: {query}",
                system_prompt=system_prompt,
                temperature=0.1
            )
            
            # Post-process with citations
            response_with_citations = self._add_citations(response_text, top_results)
            
            return {
                'text': response_with_citations,
                'sources': list(set(sources)),
                'workflow': 'advanced',
                'results': top_results,
                'context_used': True
            }
            
        except Exception as e:
            logger.error(f"Error in advanced RAG workflow: {str(e)}")
            return {
                'text': f"Error processing query: {str(e)}",
                'sources': [],
                'workflow': 'advanced',
                'results': [],
                'error': True
            }
    
    def _recursive_rag_workflow(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Recursive RAG
        Workflow: Query → Initial Retrieval → Response Planning → Targeted Retrieval → Generation
        """
        try:
            logger.info(f"Executing recursive RAG workflow for query: {query}")
            
            # Initial retrieval for planning
            initial_docs = self.chroma_service.query_documents(query, top_k)
            
            if not initial_docs['documents'][0]:
                return self._basic_rag_workflow(query, top_k)
            
            # Plan response components
            initial_context = "\n\n".join(initial_docs['documents'][0])
            response_plan = self._plan_response(query, initial_context)
            
            # Targeted retrieval for each component
            component_contexts = {}
            all_results = []
            
            for component in response_plan.get('components', []):
                sub_query = component.get('search_query', query)
                component_docs = self.chroma_service.query_documents(sub_query, 2)
                
                if component_docs['documents'][0]:
                    component_context = "\n\n".join(component_docs['documents'][0])
                    component_contexts[component['id']] = component_context
                    
                    # Add to all results
                    for i, (doc, meta, dist) in enumerate(zip(
                        component_docs['documents'][0],
                        component_docs['metadatas'][0],
                        component_docs['distances'][0]
                    )):
                        all_results.append({
                            'content': doc,
                            'metadata': meta,
                            'distance': dist,
                            'component': component['id']
                        })
            
            # Generate comprehensive response
            final_response = self._generate_structured_response(query, response_plan, component_contexts)
            
            # Extract sources
            sources = [result['metadata'].get('source', 'Unknown') for result in all_results]
            
            return {
                'text': final_response,
                'sources': list(set(sources)),
                'workflow': 'recursive',
                'results': all_results,
                'context_used': True
            }
            
        except Exception as e:
            logger.error(f"Error in recursive RAG workflow: {str(e)}")
            return self._basic_rag_workflow(query, top_k)
    
    def _adaptive_rag_workflow(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Adaptive RAG
        Workflow: Query → Analysis → Strategy Selection → Execution → Evaluation → Refinement
        """
        try:
            logger.info(f"Executing adaptive RAG workflow for query: {query}")
            
            # Analyze query complexity and type
            query_analysis = self._analyze_query(query)
            
            # Select appropriate workflow
            if query_analysis.get('is_simple_factual', False):
                initial_response = self._basic_rag_workflow(query, top_k)
            elif query_analysis.get('is_multi_part', False):
                initial_response = self._recursive_rag_workflow(query, top_k)
            else:
                initial_response = self._advanced_rag_workflow(query, top_k)
            
            # Evaluate response quality
            quality_score = self._evaluate_response_quality(query, initial_response)
            
            # Refine if needed
            if quality_score < 0.8 and not initial_response.get('error'):
                refined_response = self._refine_response(query, initial_response)
                refined_response['workflow'] = 'adaptive'
                return refined_response
            
            initial_response['workflow'] = 'adaptive'
            return initial_response
            
        except Exception as e:
            logger.error(f"Error in adaptive RAG workflow: {str(e)}")
            return self._basic_rag_workflow(query, top_k)
    
    def _expand_query(self, query: str) -> str:
        """Expand query for better recall."""
        try:
            system_prompt = """
            Expand the following query to include related terms and synonyms that would help find relevant documents.
            Keep the expansion concise and focused. Return only the expanded query.
            """
            
            expanded = LLMFactory.generate_response(
            )
            
            return expanded.strip()
            
        except Exception as e:
            logger.error(f"Error expanding query: {str(e)}")
            return query
    
    def _merge_search_results(self, semantic_results: Dict, keyword_results: Dict) -> List[Dict]:
        """Merge results from different search strategies."""
        merged = []
        seen_content = set()
        
        # Add semantic results
        if semantic_results['documents'][0]:
            for doc, meta, dist in zip(
                semantic_results['documents'][0],
                semantic_results['metadatas'][0],
                semantic_results['distances'][0]
            ):
                if doc not in seen_content:
                    merged.append({
                        'content': doc,
                        'metadata': meta,
                        'distance': dist,
                        'source_type': 'semantic'
                    })
                    seen_content.add(doc)
        
        # Add keyword results
        if keyword_results['documents'][0]:
            for doc, meta, dist in zip(
                keyword_results['documents'][0],
                keyword_results['metadatas'][0],
                keyword_results['distances'][0]
            ):
                if doc not in seen_content:
                    merged.append({
                        'content': doc,
                        'metadata': meta,
                        'distance': dist,
                        'source_type': 'keyword'
                    })
                    seen_content.add(doc)
        
        return merged
    
    def _rerank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Rerank results for relevance."""
        # Simple reranking based on distance (lower is better)
        return sorted(results, key=lambda x: x['distance'])
    
    def _add_citations(self, response: str, results: List[Dict]) -> str:
        """Add citations to response."""
        sources = []
        for i, result in enumerate(results):
            source = result['metadata'].get('source', f'Document {i+1}')
            if source not in sources:
                sources.append(source)
        
        if sources:
            citation_text = "\n\nSources: " + ", ".join(sources)
            return response + citation_text
        
        return response
    
    def _plan_response(self, query: str, context: str) -> Dict:
        """Plan response components for recursive RAG."""
        try:
            system_prompt = """
            Based on the query and initial context, plan how to structure a comprehensive response.
            Identify key components that need to be addressed and suggest search queries for each.
            Return a JSON structure with components.
            """
            
            planning_prompt = f"Query: {query}\nContext: {context[:500]}..."
            
            # For simplicity, return a basic plan
            return {
                'components': [
                    {'id': 'main', 'search_query': query},
                    {'id': 'details', 'search_query': f"{query} details examples"}
                ]
            }
            
        except Exception as e:
            logger.error(f"Error planning response: {str(e)}")
            return {'components': [{'id': 'main', 'search_query': query}]}
    
    def _generate_structured_response(self, query: str, plan: Dict, contexts: Dict) -> str:
        """Generate structured response using plan and contexts."""
        try:
            combined_context = "\n\n".join(contexts.values())
            
            system_prompt = """
            Generate a comprehensive, well-structured response using the provided contexts.
            Organize the information logically and provide a complete answer to the question.
            """
            
            return LLMFactory.generate_response(
                prompt=f"Context:\n{combined_context}\n\nQuestion: {query}",
                system_prompt=system_prompt,
                temperature=0.2
            )
            
        except Exception as e:
            logger.error(f"Error generating structured response: {str(e)}")
            return "Error generating response."
    
    def _analyze_query(self, query: str) -> Dict:
        """Analyze query complexity and type."""
        query_lower = query.lower()
        
        # Simple heuristics for query analysis
        is_simple_factual = any(word in query_lower for word in ['what is', 'who is', 'when', 'where'])
        is_multi_part = '?' in query and query.count('?') > 1 or 'and' in query_lower
        
        return {
            'is_simple_factual': is_simple_factual,
            'is_multi_part': is_multi_part,
            'length': len(query),
            'complexity': 'high' if len(query) > 100 else 'medium' if len(query) > 50 else 'low'
        }
    
    def _evaluate_response_quality(self, query: str, response: Dict) -> float:
        """Evaluate response quality."""
        # Simple quality scoring
        text = response.get('text', '')
        
        if response.get('error'):
            return 0.0
        
        if len(text) < 10:
            return 0.3
        
        if 'I couldn\'t find' in text or 'Error' in text:
            return 0.4
        
        # Check if sources are provided
        sources = response.get('sources', [])
        if sources:
            return 0.9
        
        return 0.7
    
    def _refine_response(self, query: str, initial_response: Dict) -> Dict:
        """Refine response if quality is low."""
        try:
            system_prompt = """
            The following response may need improvement. Please refine it to be more comprehensive and helpful.
            Maintain accuracy and add more detail if possible.
            """
            
            original_text = initial_response.get('text', '')
            refined_text = LLMFactory.generate_response(
                prompt=f"Original query: {query}\nOriginal response: {original_text}",
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            # Update response
            refined_response = initial_response.copy()
            refined_response['text'] = refined_text
            refined_response['refined'] = True
            
            return refined_response
            
        except Exception as e:
            logger.error(f"Error refining response: {str(e)}")
            return initial_response
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return self.chroma_service.get_collection_stats()

# Singleton instance
_rag_manager_instance = None

def get_rag_manager() -> RAGManager:
    """Get the singleton RAGManager instance."""
    global _rag_manager_instance
    if _rag_manager_instance is None:
        _rag_manager_instance = RAGManager()
    return _rag_manager_instance
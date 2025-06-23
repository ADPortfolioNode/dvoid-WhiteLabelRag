"""
SearchAgent - Specialized for document retrieval and RAG operations
"""

import logging
from typing import Dict, Any, List
from app.services.base_assistant import BaseAssistant
from app.services.rag_manager import RAGManager
from app.services.llm_factory import LLMFactory
from app.config import Config

logger = logging.getLogger(__name__)

class SearchAgent(BaseAssistant):
    """
    SearchAgent - Specialized for document retrieval and RAG operations.
    Handles query expansion, multi-document retrieval, result ranking, and source attribution.
    """
    
    def __init__(self):
        super().__init__("SearchAgent")
        self.rag_manager = RAGManager()
        self.llm = LLMFactory.get_llm()
        self.config = Config.ASSISTANT_CONFIGS['SearchAgent']
    
    def handle_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle search requests and return formatted results."""
        try:
            # Validate input
            is_valid, validation_message = self._validate_input(message)
            if not is_valid:
                return self.report_failure(validation_message)
            
            # Update status
            self._update_status("running", 10, "Processing search query...")
            
            # Extract search parameters from context if provided
            search_params = self._extract_search_parameters(message, context)
            
            # Get collection stats
            self._update_status("running", 20, "Checking document collection...")
            collection_stats = self.rag_manager.get_collection_stats()
            
            if collection_stats.get('documents_count', 0) == 0:
                return self.report_failure("No documents available for search. Please upload some documents first.")
            
            # Execute search with appropriate workflow
            self._update_status("running", 40, "Searching documents...")
            workflow_type = search_params.get('workflow', 'adaptive')
            n_results = search_params.get('top_k', 5)
            
            results = self.rag_manager.query_documents(
                query=message,
                n_results=n_results
            )
            
            # Format and enhance results
            self._update_status("running", 80, "Formatting search results...")
            formatted_results = self._format_search_results(results, message)
            
            return self.report_success(
                text=formatted_results,
                additional_data={
                    'sources': results.get('sources', []),
                    'workflow_used': results.get('workflow', workflow_type),
                    'results_count': len(results.get('results', [])),
                    'collection_stats': collection_stats
                }
            )
            
        except Exception as e:
            logger.error(f"Error in SearchAgent.handle_message: {str(e)}")
            return self.report_failure(f"Search error: {str(e)}")
    
    def _extract_search_parameters(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract search parameters from message and context."""
        params = {
            'workflow': 'adaptive',
            'top_k': 5,
            'min_relevance': 0.7
        }
        
        # Override with context parameters if provided
        if context:
            params.update({
                'workflow': context.get('workflow', params['workflow']),
                'top_k': context.get('top_k', params['top_k']),
                'min_relevance': context.get('min_relevance', params['min_relevance'])
            })
        
        # Extract parameters from message text
        message_lower = message.lower()
        
        # Check for workflow hints in message
        if 'detailed' in message_lower or 'comprehensive' in message_lower:
            params['workflow'] = 'advanced'
        elif 'quick' in message_lower or 'brief' in message_lower:
            params['workflow'] = 'basic'
        elif 'complex' in message_lower or 'multi-part' in message_lower:
            params['workflow'] = 'recursive'
        
        # Check for result count hints
        if 'more results' in message_lower or 'all' in message_lower:
            params['top_k'] = 10
        elif 'few' in message_lower or 'top' in message_lower:
            params['top_k'] = 3
        
        return params
    
    def _format_search_results(self, results: Dict[str, Any], query: str) -> str:
        """Format search results into a readable response."""
        try:
            if results.get('error'):
                return f"Search encountered an error: {results.get('text', 'Unknown error')}"
            
            response_text = results.get('text', '')
            sources = results.get('sources', [])
            workflow = results.get('workflow', 'basic')
            search_results = results.get('results', [])
            
            if not response_text and not search_results:
                return self._generate_no_results_response(query)
            
            # If we have a generated response, use it
            if response_text:
                formatted_response = response_text
            else:
                # Generate response from raw results
                formatted_response = self._generate_response_from_results(search_results, query)
            
            # Add metadata about the search
            metadata_info = self._format_search_metadata(workflow, len(search_results), sources)
            
            return f"{formatted_response}\n\n{metadata_info}"
            
        except Exception as e:
            logger.error(f"Error formatting search results: {str(e)}")
            return f"Found relevant information but encountered an error formatting the response: {str(e)}"
    
    def _generate_no_results_response(self, query: str) -> str:
        """Generate a helpful response when no results are found."""
        try:
            system_prompt = """
            The user's search query didn't return any relevant results from the document collection.
            Provide a helpful response that:
            1. Acknowledges that no specific documents were found
            2. Suggests alternative search terms or approaches
            3. Offers to help with related topics if possible
            4. Remains encouraging and helpful
            """
            
            response = LLMFactory.generate_response(
                prompt=f"User searched for: {query}",
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating no results response: {str(e)}")
            return "I couldn't find any documents matching your search. Try using different keywords or check if relevant documents have been uploaded."
    
    def _generate_response_from_results(self, search_results: List[Dict], query: str) -> str:
        """Generate a response from raw search results."""
        try:
            if not search_results:
                return "No relevant information found."
            
            # Combine content from top results
            context_parts = []
            for i, result in enumerate(search_results[:3]):  # Use top 3 results
                content = result.get('content', '')
                source = result.get('metadata', {}).get('source', f'Document {i+1}')
                context_parts.append(f"From {source}:\n{content}")
            
            context = "\n\n".join(context_parts)
            
            system_prompt = self.config['system_prompt']
            
            response = LLMFactory.generate_response(
                prompt=f"Based on the following information, answer the user's question: {query}\n\nInformation:\n{context}",
                system_prompt=system_prompt,
                temperature=0.2
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response from results: {str(e)}")
            return "Found relevant information but encountered an error generating the response."
    
    def _format_search_metadata(self, workflow: str, result_count: int, sources: List[str]) -> str:
        """Format metadata about the search."""
        metadata_parts = []
        
        # Add workflow information
        workflow_descriptions = {
            'basic': 'Quick search',
            'advanced': 'Comprehensive search',
            'recursive': 'Multi-stage search',
            'adaptive': 'Smart search'
        }
        
        workflow_desc = workflow_descriptions.get(workflow, workflow)
        metadata_parts.append(f"Search method: {workflow_desc}")
        
        # Add result count
        if result_count > 0:
            metadata_parts.append(f"Found {result_count} relevant passages")
        
        # Add sources
        if sources:
            unique_sources = list(set(sources))
            if len(unique_sources) == 1:
                metadata_parts.append(f"Source: {unique_sources[0]}")
            else:
                metadata_parts.append(f"Sources: {', '.join(unique_sources[:3])}")
                if len(unique_sources) > 3:
                    metadata_parts[-1] += f" and {len(unique_sources) - 3} more"
        
        return " | ".join(metadata_parts)
    
    def search_with_filters(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search with additional filters."""
        try:
            self._update_status("running", 20, "Applying search filters...")
            
            # Apply filters to ChromaDB query
            where_clause = None
            if filters:
                where_clause = {}
                if 'source' in filters:
                    where_clause['source'] = filters['source']
                if 'file_type' in filters:
                    where_clause['file_type'] = filters['file_type']
            
            # Execute filtered search
            results = self.rag_manager.chroma_service.query_documents(
                query=query,
                n_results=filters.get('top_k', 5),
                where=where_clause
            )
            
            # Format results
            formatted_response = self._format_raw_chroma_results(results, query)
            
            return self.report_success(
                text=formatted_response,
                additional_data={
                    'filters_applied': filters,
                    'results_count': len(results.get('documents', [[]])[0])
                }
            )
            
        except Exception as e:
            logger.error(f"Error in filtered search: {str(e)}")
            return self.report_failure(f"Filtered search error: {str(e)}")
    
    def _format_raw_chroma_results(self, results: Dict[str, Any], query: str) -> str:
        """Format raw ChromaDB results."""
        try:
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            if not documents:
                return "No results found with the applied filters."
            
            # Generate response from documents
            context = "\n\n".join(documents[:3])
            sources = [meta.get('source', 'Unknown') for meta in metadatas[:3]]
            
            system_prompt = self.config['system_prompt']
            
            response = LLMFactory.generate_response(
                prompt=f"Based on the following information, answer: {query}\n\nInformation:\n{context}",
                system_prompt=system_prompt,
                temperature=0.2
            )
            
            # Add source information
            if sources:
                unique_sources = list(set(sources))
                response += f"\n\nSources: {', '.join(unique_sources)}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting raw results: {str(e)}")
            return "Found results but encountered an error formatting them."
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on partial query."""
        try:
            # This could be enhanced with actual document analysis
            # For now, provide basic suggestions
            suggestions = []
            
            if len(partial_query) >= 3:
                # Simple keyword-based suggestions
                common_terms = ['what', 'how', 'when', 'where', 'why', 'who']
                for term in common_terms:
                    if term.startswith(partial_query.lower()):
                        suggestions.append(f"{term} is")
                        suggestions.append(f"{term} does")
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {str(e)}")
            return []

# Singleton instance
_search_agent_instance = None

def get_search_agent_instance() -> SearchAgent:
    """Get the singleton SearchAgent instance."""
    global _search_agent_instance
    if _search_agent_instance is None:
        _search_agent_instance = SearchAgent()
    return _search_agent_instance
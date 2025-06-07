import logging
import requests
from typing import Dict, Any, List, Optional
from app.services.base_assistant import BaseAssistant
from app.services.llm_factory import LLMFactory
from app.config import Config

logger = logging.getLogger(__name__)

class InternetSearchAgent(BaseAssistant):
    """
    InternetSearchAgent - Provides modular internet search capabilities
    using external search APIs.
    """

    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None):
        super().__init__("InternetSearchAgent")
        # Configuration for external search API (e.g., Google Custom Search)
        self.api_key = api_key or Config.INTERNET_SEARCH_API_KEY
        self.search_engine_id = search_engine_id or Config.INTERNET_SEARCH_ENGINE_ID
        self.config = Config.ASSISTANT_CONFIGS.get('InternetSearchAgent', {})
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Perform an internet search using the configured external API.
        Returns a dictionary with search results and metadata.
        """
        try:
            if not self.api_key or not self.search_engine_id:
                error_msg = "API key or Search Engine ID not configured."
                logger.error(error_msg)
                return self.report_failure(error_msg)

            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': num_results
            }

            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            items = data.get('items', [])
            results = []
            for item in items:
                results.append({
                    'title': item.get('title'),
                    'link': item.get('link'),
                    'snippet': item.get('snippet'),
                    'displayLink': item.get('displayLink')
                })

            formatted_response = self._format_results(results, query)

            return self.report_success(
                text=formatted_response,
                additional_data={
                    'results': results,
                    'total_results': data.get('searchInformation', {}).get('totalResults', '0')
                }
            )

        except requests.RequestException as e:
            logger.error(f"Internet search request failed: {str(e)}")
            return self.report_failure(f"Internet search request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error in InternetSearchAgent.search: {str(e)}")
            return self.report_failure(f"Search error: {str(e)}")

    def _format_results(self, results: List[Dict[str, Any]], query: str) -> str:
        """
        Format the search results into a readable string response.
        """
        if not results:
            return f"No internet search results found for query: {query}"

        response_lines = [f"Internet search results for: '{query}':\n"]
        for i, result in enumerate(results, start=1):
            response_lines.append(f"{i}. {result['title']}\n   {result['snippet']}\n   Link: {result['link']}\n")

        return "\n".join(response_lines)

    def handle_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Implement abstract method from BaseAssistant.
        Calls search() method with the message as query.
        """
        return self.search(message)

# Singleton instance
_internet_search_agent_instance = None

def get_internet_search_agent_instance() -> InternetSearchAgent:
    global _internet_search_agent_instance
    if _internet_search_agent_instance is None:
        _internet_search_agent_instance = InternetSearchAgent()
    return _internet_search_agent_instance

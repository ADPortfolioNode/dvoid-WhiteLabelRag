import logging
from typing import Dict, Any
from app.services.llm_factory import LLMFactory

logger = logging.getLogger(__name__)

class FileManager:
    """
    FileManager service to handle file operations including document summarization.
    """

    def __init__(self):
        self.llm = LLMFactory.get_llm('summarization')

    def summarize_document(self, document_text: str) -> Dict[str, Any]:
        """
        Summarize the given document text using LLM.

        Args:
            document_text (str): The full text content of the document.

        Returns:
            Dict[str, Any]: A dictionary with summary text and metadata.
        """
        try:
            system_prompt = """
            You are a document summarization assistant. Provide a concise and informative summary of the given document text.
            """

            prompt = f"Please summarize the following document:\n\n{document_text}"

            summary = LLMFactory.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                task='summarization'
            )

            return {
                'success': True,
                'summary': summary
            }
        except Exception as e:
            logger.error(f"Error summarizing document: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Singleton instance
_file_manager_instance = None

def get_file_manager_instance() -> FileManager:
    global _file_manager_instance
    if _file_manager_instance is None:
        _file_manager_instance = FileManager()
    return _file_manager_instance

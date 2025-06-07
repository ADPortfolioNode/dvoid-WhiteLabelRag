import os
import logging
from typing import Dict, Any, Optional
from app.services.base_assistant import BaseAssistant
from app.config import Config

logger = logging.getLogger(__name__)

class MultimediaAgent(BaseAssistant):
    """
    MultimediaAgent - Handles uploads, downloads, and processing of images, audio, and video files.
    Provides modular multimedia processing capabilities accessible to any assistant.
    """

    def __init__(self):
        super().__init__("MultimediaAgent")
        self.uploads_path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            Config.UPLOAD_FOLDER
        ))
        os.makedirs(self.uploads_path, exist_ok=True)

    def handle_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle multimedia-related requests.
        This is a placeholder for message-based commands.
        """
        # For now, just return a help message
        return self._provide_help()

    def is_supported_format(self, filename: str) -> bool:
        """
        Check if the file extension is supported for multimedia processing.
        Only accepts actual multimedia files (images, audio, video).
        """
        ext = os.path.splitext(filename)[1].lower().strip('.')
        multimedia_extensions = {
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff',  # Images
            'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a',           # Audio
            'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'    # Video
        }
        return ext in multimedia_extensions

    def save_file(self, file_storage) -> Dict[str, Any]:
        """
        Save an uploaded file to the uploads directory.
        file_storage is expected to be a Werkzeug FileStorage object.
        """
        filename = file_storage.filename
        if not self.is_supported_format(filename):
            return self.report_failure(f"File type not supported: {filename}")

        save_path = os.path.join(self.uploads_path, filename)
        try:
            file_storage.save(save_path)
            return self.report_success(f"File '{filename}' uploaded successfully.", {'filename': filename})
        except Exception as e:
            logger.error(f"Error saving file {filename}: {str(e)}")
            return self.report_failure(f"Error saving file: {str(e)}")

    def _provide_help(self) -> Dict[str, Any]:
        help_text = (
            "Multimedia Operations Help:\n\n"
            "I can help you with the following multimedia operations:\n"
            "📁 Upload images, audio, and video files.\n"
            "🔍 Process multimedia files for analysis or retrieval.\n"
            "🗑️ Delete multimedia files.\n"
            "ℹ️ Get information about multimedia files.\n\n"
            "Supported file types include common image, audio, and video formats.\n"
            "Examples:\n"
            "- Upload a file\n"
            "- Show info about image.jpg\n"
            "- Delete video.mp4\n"
        )
        return self.report_success(help_text)

# Singleton instance
_multimedia_agent_instance = None

def get_multimedia_agent_instance() -> MultimediaAgent:
    global _multimedia_agent_instance
    if _multimedia_agent_instance is None:
        _multimedia_agent_instance = MultimediaAgent()
    return _multimedia_agent_instance

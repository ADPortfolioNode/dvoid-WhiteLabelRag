"""
Base Assistant class for all specialized assistants
"""

import logging
from datetime import datetime

class BaseAssistant:
    """Base class for all assistants in the WhiteLabelRAG system."""
    
    def __init__(self, name):
        self.name = name
        self.status = "idle"
        self.progress = 0
        self.details = "Initialized"

    def _update_status(self, status, progress, details):
        self.status = status
        self.progress = progress
        self.details = details
        # Optionally emit WebSocket event here

    def report_success(self, text, additional_data=None):
        self._update_status("completed", 100, "Task completed successfully")
        result = {
            "text": text,
            "assistant": self.name,
            "timestamp": datetime.now().isoformat()
        }
        if additional_data:
            result.update(additional_data)
        return result

    def report_failure(self, error_message):
        self._update_status("failed", 100, error_message)
        return {
            "text": error_message,
            "assistant": self.name,
            "timestamp": datetime.now().isoformat(),
            "error": True
        }
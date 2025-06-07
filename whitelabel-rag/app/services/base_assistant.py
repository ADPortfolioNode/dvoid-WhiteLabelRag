"""
Base Assistant class for all specialized assistants
"""

import logging
from datetime import datetime
from abc import ABC, abstractmethod
from app import socketio

logger = logging.getLogger(__name__)

class BaseAssistant(ABC):
    """Base class for all assistants in the WhiteLabelRAG system."""
    
    def __init__(self, name):
        self.name = name
        self.status = "idle"
        self.progress = 0
        self.details = "Initialized"
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
    def _update_status(self, status, progress, details):
        """Update assistant status and emit WebSocket event."""
        self.status = status
        self.progress = progress
        self.details = details
        
        self.logger.info(f"Status update: {status} ({progress}%) - {details}")
        
        # Emit WebSocket event with status update
        try:
            socketio.emit('assistant_status_update', {
                'assistant_id': id(self),
                'name': self.name,
                'status': status,
                'progress': progress,
                'details': details,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            self.logger.error(f"Error emitting status update: {str(e)}")
            
    def report_success(self, text, additional_data=None):
        """Report successful completion of task."""
        self._update_status("completed", 100, "Task completed successfully")
        
        result = {
            "text": text,
            "assistant": self.name,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
        if additional_data:
            result.update(additional_data)
            
        return result
        
    def report_failure(self, error_message):
        """Report task failure."""
        self._update_status("failed", 100, error_message)
        
        return {
            "text": error_message,
            "assistant": self.name,
            "timestamp": datetime.now().isoformat(),
            "error": True,
            "success": False
        }
    
    def report_progress(self, progress, details):
        """Report task progress."""
        self._update_status("running", progress, details)
    
    @abstractmethod
    def handle_message(self, message, context=None):
        """Handle incoming message. Must be implemented by subclasses."""
        pass
    
    def _extract_intent(self, message):
        """Extract intent from message. Can be overridden by subclasses."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['search', 'find', 'look for', 'query']):
            return 'search'
        elif any(word in message_lower for word in ['upload', 'file', 'document']):
            return 'file_operation'
        elif any(word in message_lower for word in ['execute', 'run', 'function', 'call']):
            return 'function_execution'
        else:
            return 'general'
    
    def _validate_input(self, message):
        """Validate input message."""
        if message is None or not isinstance(message, str):
            return False, "Invalid message format"
        
        if len(message.strip()) == 0:
            return False, "Empty message"
        
        if len(message) > 10000:  # Reasonable limit
            return False, "Message too long"
        
        return True, "Valid"
    
    def get_status(self):
        """Get current assistant status."""
        return {
            'name': self.name,
            'status': self.status,
            'progress': self.progress,
            'details': self.details
        }
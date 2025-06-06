"""
Conversation store for managing user sessions and conversation history
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

class Conversation:
    """Represents a conversation session."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: List[Dict[str, Any]] = []
        self.user_info: Dict[str, Any] = {}
        self.conversation_state = "information_gathering"
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.max_messages = 20  # Keep last 20 messages
    
    def add_message(self, role: str, content: str, sources: List[str] = None):
        """Add a message to the conversation."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "sources": sources or []
        }
        
        self.messages.append(message)
        self.last_activity = datetime.now()
        
        # Keep only the last max_messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        
        logger.debug(f"Added {role} message to conversation {self.session_id}")
    
    def get_recent_messages(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages from the conversation."""
        return self.messages[-count:] if self.messages else []
    
    def get_context_string(self, max_length: int = 2000) -> str:
        """Get conversation context as a string."""
        context_parts = []
        total_length = 0
        
        # Start from most recent messages and work backwards
        for message in reversed(self.messages):
            message_text = f"{message['role']}: {message['content']}"
            if total_length + len(message_text) > max_length:
                break
            context_parts.insert(0, message_text)
            total_length += len(message_text)
        
        return "\n".join(context_parts)
    
    def set_state(self, state: str):
        """Set conversation state."""
        self.conversation_state = state
        self.last_activity = datetime.now()
    
    def is_expired(self, timeout_hours: int = 24) -> bool:
        """Check if conversation has expired."""
        return datetime.now() - self.last_activity > timedelta(hours=timeout_hours)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary."""
        return {
            "session_id": self.session_id,
            "messages": self.messages,
            "user_info": self.user_info,
            "conversation_state": self.conversation_state,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }

class ConversationStore:
    """Store for managing conversation sessions."""
    
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.cleanup_interval_hours = 24
    
    def get_conversation(self, session_id: str) -> Conversation:
        """Get or create a conversation for the session."""
        if session_id not in self.conversations:
            self.conversations[session_id] = Conversation(session_id)
            logger.info(f"Created new conversation for session {session_id}")
        else:
            # Update last activity
            self.conversations[session_id].last_activity = datetime.now()
        
        return self.conversations[session_id]
    
    def delete_conversation(self, session_id: str) -> bool:
        """Delete a conversation."""
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"Deleted conversation for session {session_id}")
            return True
        return False
    
    def cleanup_expired_conversations(self, timeout_hours: int = 24):
        """Remove expired conversations."""
        expired_sessions = []
        
        for session_id, conversation in self.conversations.items():
            if conversation.is_expired(timeout_hours):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.conversations[session_id]
            logger.info(f"Cleaned up expired conversation {session_id}")
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired conversations")
    
    def get_active_conversations_count(self) -> int:
        """Get count of active conversations."""
        return len(self.conversations)
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get statistics about conversations."""
        total_conversations = len(self.conversations)
        total_messages = sum(len(conv.messages) for conv in self.conversations.values())
        
        if total_conversations > 0:
            avg_messages_per_conversation = total_messages / total_conversations
        else:
            avg_messages_per_conversation = 0
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "avg_messages_per_conversation": round(avg_messages_per_conversation, 2)
        }
    
    def export_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export a conversation as JSON."""
        if session_id in self.conversations:
            return self.conversations[session_id].to_dict()
        return None
    
    def import_conversation(self, conversation_data: Dict[str, Any]) -> bool:
        """Import a conversation from JSON data."""
        try:
            session_id = conversation_data["session_id"]
            conversation = Conversation(session_id)
            
            conversation.messages = conversation_data.get("messages", [])
            conversation.user_info = conversation_data.get("user_info", {})
            conversation.conversation_state = conversation_data.get("conversation_state", "information_gathering")
            
            # Parse timestamps
            if "created_at" in conversation_data:
                conversation.created_at = datetime.fromisoformat(conversation_data["created_at"])
            if "last_activity" in conversation_data:
                conversation.last_activity = datetime.fromisoformat(conversation_data["last_activity"])
            
            self.conversations[session_id] = conversation
            logger.info(f"Imported conversation for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing conversation: {str(e)}")
            return False

# Singleton instance
_conversation_store_instance = None

def get_conversation_store() -> ConversationStore:
    """Get the singleton ConversationStore instance."""
    global _conversation_store_instance
    if _conversation_store_instance is None:
        _conversation_store_instance = ConversationStore()
    return _conversation_store_instance
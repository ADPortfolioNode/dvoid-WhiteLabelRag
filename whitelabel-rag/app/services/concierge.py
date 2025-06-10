"""
Concierge Agent - Main orchestrator and entry point for user interactions
"""

import logging
import uuid
from typing import Dict, Any, Optional
from app.services.base_assistant import BaseAssistant
from app.services.llm_factory import LLMFactory
from app.services.conversation_store import get_conversation_store
from app.services.rag_manager import get_rag_manager
from app.config import Config

logger = logging.getLogger(__name__)

class Concierge(BaseAssistant):
    """
    Concierge Agent - Main orchestrator for all user interactions.
    Handles conversation management, intent classification, and routing to specialized agents.
    """
    
    def __init__(self):
        super().__init__("Concierge")
        self.conversation_store = get_conversation_store()
        self.rag_manager = get_rag_manager()
        self.config = Config.ASSISTANT_CONFIGS['Concierge']
        
        # Greeting message on initialization
        self.greeting = "Hello! How can I assist you today?"
        
    
        self.direct_functions = {
            'get_time': self._get_current_time,
            'get_stats': self._get_system_stats,
            'help': self._get_help
        }
    
    def get_greeting(self) -> str:
        """Return the greeting message."""
        return self.greeting
    def handle_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point for handling user messages.
        Implements the hierarchical workflow architecture.
        """
        try:
            # Validate input
            is_valid, validation_message = self._validate_input(message)
            if not is_valid:
                return self.report_failure(validation_message)
            
            # Get or create session
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Update status
            self._update_status("running", 10, "Processing message...")
            
            # Get conversation context
            conversation = self.conversation_store.get_conversation(session_id)
            
            # Check conversation state for username prompt
            if conversation.conversation_state == "awaiting_username":
                username = message.strip()
                from datetime import datetime
                user_id = f"{username}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                conversation.user_info['user_id'] = user_id
                conversation.user_info['username'] = username
                
                # Save initial topic name dialogue encoded into RAG
                topic_dialogue = f"User {username} started session with user_id {user_id}."
                self.rag_manager.store_document_chunk(
                    content=topic_dialogue,
                    metadata={"user_id": user_id, "username": username, "session_id": session_id}
                )
                
                # Update conversation state to active
                conversation.set_state("active")
                
                # Add user message to conversation
                conversation.add_message("user", message)
                
                # Respond with greeting and confirmation
                response_text = f"Hello {username}! How can I assist you today?"
                conversation.add_message("assistant", response_text)
                
                self._update_status("completed", 100, "Username received and session started")
                return self.report_success(text=response_text)
            
            # If new session, prompt for username
            if len(conversation.messages) == 0:
                conversation.set_state("awaiting_username")
                prompt_text = "Welcome! Please tell me your name to get started."
                conversation.add_message("assistant", prompt_text)
                self._update_status("completed", 100, "Prompted for username")
                return self.report_success(text=prompt_text)
            
            # Add user message to conversation
            conversation.add_message("user", message)
            
            # Classify the message intent
            self._update_status("running", 30, "Analyzing message intent...")
            intent = self._classify_intent(message, conversation)
            
            # Process based on intent using hierarchical workflow
            self._update_status("running", 50, f"Processing {intent} request...")
            
            if intent == "document_search":
                response = self._handle_document_search(message, conversation)
            elif intent == "task_request":
                response = self._handle_task_decomposition(message, conversation)
            elif intent == "meta":
                response = self._handle_meta_query(message, conversation)
            elif intent == "simple_query":
                response = self._handle_simple_query(message, conversation)
            else:
                response = self._generate_direct_response(message, conversation)
            
            # Add assistant response to conversation
            conversation.add_message("assistant", response.get('text', ''), response.get('sources', []))
            
            # Update final status
            self._update_status("completed", 100, "Message processed successfully")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in Concierge.handle_message: {str(e)}")
            return self.report_failure(f"Error processing message: {str(e)}")
    
    def _classify_intent(self, message: str, conversation) -> str:
        """Classify user message intent using LLM."""
        try:
            # Get conversation context for better classification
            context = conversation.get_context_string(500)
            
            system_prompt = """
            Classify the user's message into one of these categories based on the message and conversation context:
            
            - simple_query: Direct question that can be answered with general knowledge, system functions (time, stats), or brief response
            - document_search: Request to find specific information in documents or knowledge base
            - task_request: Complex multi-step task that requires decomposition and planning
            - clarification: User asking for clarification or followup on previous response
            - feedback: User providing feedback on previous response
            - meta: Question about the system itself, capabilities, or how it works
            
            Note: System function requests like "show stats", "what time is it", "help" should be classified as simple_query.
            
            Consider the conversation context and respond with only the category name.
            """
            
            prompt = f"Conversation context:\n{context}\n\nCurrent message: {message}"
            
            intent = LLMFactory.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1,
                task='classification'
            ).strip().lower()
            
            # Validate intent
            valid_intents = ['simple_query', 'document_search', 'task_request', 'clarification', 'feedback', 'meta']
            if intent not in valid_intents:
                intent = 'simple_query'  # Default fallback
            
            logger.info(f"Classified intent as: {intent}")
            return intent
            
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            return 'simple_query'  # Default fallback
    
    def _handle_document_search(self, message: str, conversation) -> Dict[str, Any]:
        """Handle document search requests using SearchAgent."""
        try:
            self._update_status("running", 60, "Searching documents...")
            
            # Use RAG manager for document search
            results = self.rag_manager.query_documents(message, workflow_type="adaptive")
            
            if results.get('error'):
                return self.report_failure("Error searching documents")
            
            return self.report_success(
                text=results.get('text', 'No relevant documents found.'),
                additional_data={
                    'sources': results.get('sources', []),
                    'workflow': results.get('workflow', 'basic'),
                    'context_used': results.get('context_used', False)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in document search: {str(e)}")
            return self.report_failure("Error searching documents")
    
    def _handle_task_decomposition(self, message: str, conversation) -> Dict[str, Any]:
        """Handle complex task requests that require decomposition using TaskAssistant."""
        try:
            self._update_status("running", 60, "Delegating to TaskAssistant...")
            
            # Import TaskAssistant
            from app.services.task_assistant import get_task_assistant_instance
            
            # Get TaskAssistant instance
            task_assistant = get_task_assistant_instance()
            
            # Prepare context for TaskAssistant
            context = {
                'session_id': conversation.session_id if hasattr(conversation, 'session_id') else None,
                'conversation_context': conversation.get_context_string(500)
            }
            
            # Delegate to TaskAssistant
            result = task_assistant.handle_message(message, context)
            
            if result.get('error'):
                # Fallback to simple response if TaskAssistant fails
                logger.warning(f"TaskAssistant failed, falling back to simple response: {result.get('text')}")
                return self._generate_direct_response(message, conversation)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in task decomposition: {str(e)}")
            # Fallback to simple response
            return self._generate_direct_response(message, conversation)
    
    def _handle_meta_query(self, message: str, conversation) -> Dict[str, Any]:
        """Handle questions about the system itself."""
        try:
            system_prompt = """
            You are the WhiteLabelRAG Concierge. Answer questions about the system's capabilities,
            how it works, and what it can do. Be helpful and informative.
            
            Key capabilities:
            - Document search and retrieval using RAG (Retrieval-Augmented Generation)
            - Conversational AI with context awareness
            - File upload and processing (PDF, DOCX, TXT, MD, CSV)
            - Task decomposition and execution
            - Real-time status updates
            """
            
            response_text = LLMFactory.generate_response(
                prompt=message,
                system_prompt=system_prompt,
                temperature=0.3,
                task=self.config['task']
            )
            
            return self.report_success(text=response_text)
            
        except Exception as e:
            logger.error(f"Error handling meta query: {str(e)}")
            return self.report_failure("Error processing system query")
    
    def _handle_simple_query(self, message: str, conversation) -> Dict[str, Any]:
        """Handle simple queries that don't require document search."""
        try:
            # Check for direct function calls first
            direct_response = self._check_direct_functions(message)
            if direct_response:
                return self.report_success(text=direct_response)
            
            # Check if we have relevant documents
            collection_stats = self.rag_manager.get_collection_stats()
            
            if collection_stats.get('documents_count', 0) > 0:
                # Try a quick document search to see if we have relevant information
                results = self.rag_manager.query_documents(message, n_results=2, workflow_type="basic")
                
                if results.get('sources') and not results.get('error'):
                    # We found relevant documents, use them
                    return self.report_success(
                        text=results.get('text', ''),
                        additional_data={
                            'sources': results.get('sources', []),
                            'context_used': True
                        }
                    )
            
            # No relevant documents or no documents at all, provide general response
            context = conversation.get_context_string(500)
            
            system_prompt = """
            You are the WhiteLabelRAG Concierge assistant. Provide a clear, informative response to the user's question.
            You have access to document search capabilities and can help with various tasks.
            Be conversational and helpful. If you don't know something, say so honestly.
            """
            
            prompt = f"Conversation context:\n{context}\n\nQuestion: {message}" if context else message
            
            response_text = LLMFactory.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                task=self.config['task']
            )
            
            return self.report_success(text=response_text)
            
        except Exception as e:
            logger.error(f"Error handling simple query: {str(e)}")
            return self.report_failure("Error processing query")
    
    def _generate_direct_response(self, message: str, conversation) -> Dict[str, Any]:
        """Generate a direct conversational response."""
        try:
            context = conversation.get_context_string(800)
            
            system_prompt = self.config['system_prompt']
            
            prompt = f"Conversation context:\n{context}\n\nUser: {message}" if context else message
            
            response_text = LLMFactory.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=self.config['temperature'],
                task=self.config['task']
            )
            
            return self.report_success(text=response_text)
            
        except Exception as e:
            logger.error(f"Error generating direct response: {str(e)}")
            return self.report_failure("Error generating response")
    
    def _check_direct_functions(self, message: str) -> Optional[str]:
        """Check if message matches a direct function and execute it."""
        message_lower = message.lower().strip()
        
        # Check for system stats requests
        if any(phrase in message_lower for phrase in [
            'system stats', 'system statistics', 'show stats', 'get stats',
            'system status', 'show system stats', 'system info'
        ]):
            return self._get_system_stats()
        
        # Check for time requests
        elif any(phrase in message_lower for phrase in [
            'what time', 'current time', 'time is it', 'show time'
        ]):
            return self._get_current_time()
        
        # Check for help requests
        elif any(phrase in message_lower for phrase in [
            'help', 'what can you do', 'capabilities', 'commands'
        ]):
            return self._get_help()
        
        return None
    
    def _get_current_time(self) -> str:
        """Get current time."""
        from datetime import datetime
        return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    def _get_system_stats(self) -> str:
        """Get system statistics."""
        try:
            collection_stats = self.rag_manager.get_collection_stats()
            conversation_stats = self.conversation_store.get_conversation_stats()
            
            stats = f"""System Statistics:
            
Documents: {collection_stats.get('documents_count', 0)} chunks indexed
Active Conversations: {conversation_stats.get('total_conversations', 0)}
Total Messages: {conversation_stats.get('total_messages', 0)}
Average Messages per Conversation: {conversation_stats.get('avg_messages_per_conversation', 0)}
            """
            
            return stats.strip()
            
        except Exception as e:
            return f"Error getting system stats: {str(e)}"
    
    def _get_help(self) -> str:
        """Get help information."""
        return """WhiteLabelRAG Help:

I can help you with:
• Searching through uploaded documents
• Answering questions using available knowledge
• Processing and analyzing files
• Having conversations with context awareness

Commands:
• Upload documents using the file upload interface
• Ask questions about your documents
• Request system statistics
• Ask about my capabilities

Just type your question or request naturally!"""

# Singleton instance
_concierge_instance = None

def get_concierge_instance() -> Concierge:
    """Get the singleton Concierge instance."""
    global _concierge_instance
    if _concierge_instance is None:
        _concierge_instance = Concierge()
    return _concierge_instance
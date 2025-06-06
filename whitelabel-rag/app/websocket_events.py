"""
WebSocket event handlers for real-time communication
"""

import logging
from flask_socketio import emit, disconnect
from flask import request

logger = logging.getLogger(__name__)

def register_websocket_events(socketio):
    """Register WebSocket event handlers."""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        logger.info(f"Client connected: {request.sid}")
        emit('connection_response', {
            'status': 'connected',
            'message': 'Successfully connected to WhiteLabelRAG',
            'session_id': request.sid
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        logger.info(f"Client disconnected: {request.sid}")
    
    @socketio.on('health_check')
    def handle_health_check():
        """Handle health check ping."""
        emit('health_check_response', {
            'status': 'healthy',
            'timestamp': str(datetime.now())
        })
    
    @socketio.on('chat_message')
    def handle_chat_message(data):
        """Handle incoming chat messages."""
        try:
            from datetime import datetime
            
            # Validate input data
            if not data or not isinstance(data, dict):
                logger.error("Invalid message data received")
                emit('chat_response', {
                    'text': 'Invalid message format.',
                    'error': True,
                    'timestamp': str(datetime.now())
                })
                return
            
            message = data.get('message', '')
            session_id = data.get('session_id', request.sid)
            
            if not message.strip():
                logger.warning("Empty message received")
                emit('chat_response', {
                    'text': 'Please enter a message.',
                    'error': True,
                    'timestamp': str(datetime.now())
                })
                return
            
            logger.info(f"Received message from {session_id}: {message[:100]}...")
            
            # Emit status update
            emit('assistant_status', {
                'status': 'processing',
                'progress': 10,
                'details': 'Processing your message...'
            })
            
            # Process message through Concierge with timeout protection
            try:
                from app.services.concierge import get_concierge_instance
                concierge = get_concierge_instance()
                response = concierge.handle_message(message, session_id)
                
                # Validate response
                if not response or not isinstance(response, dict):
                    raise ValueError("Invalid response from Concierge")
                
            except Exception as processing_error:
                logger.error(f"Error in message processing: {str(processing_error)}")
                response = {
                    'text': 'I encountered an error while processing your message. Please try again.',
                    'error': True,
                    'timestamp': str(datetime.now())
                }
            
            # Emit response
            emit('chat_response', {
                'text': response.get('text', 'No response generated.'),
                'sources': response.get('sources', []),
                'timestamp': response.get('timestamp', str(datetime.now())),
                'session_id': session_id,
                'error': response.get('error', False)
            })
            
            # Emit completion status
            status = 'error' if response.get('error') else 'completed'
            emit('assistant_status', {
                'status': status,
                'progress': 100,
                'details': 'Error processing message' if response.get('error') else 'Message processed successfully'
            })
            
        except Exception as e:
            logger.error(f"Critical error in chat message handler: {str(e)}")
            import traceback
            traceback.print_exc()
            
            try:
                from datetime import datetime
                emit('chat_response', {
                    'text': 'A critical error occurred. Please refresh the page and try again.',
                    'error': True,
                    'timestamp': str(datetime.now())
                })
                
                emit('assistant_status', {
                    'status': 'error',
                    'progress': 100,
                    'details': 'Critical error occurred'
                })
            except:
                # If even emitting fails, just log it
                logger.error("Failed to emit error response")
    
    @socketio.on_error_default
    def default_error_handler(e):
        """Handle WebSocket errors."""
        logger.error(f"WebSocket error: {str(e)}")
        emit('error', {'message': 'An error occurred'})

from datetime import datetime
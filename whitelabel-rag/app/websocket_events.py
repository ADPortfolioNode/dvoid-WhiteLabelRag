"""
WebSocket event handlers for real-time communication using FastAPI WebSocket
"""

import logging
from fastapi import WebSocket, WebSocketDisconnect
from fastapi import APIRouter
from datetime import datetime
from app.services.concierge import get_concierge_instance

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client connected: {client_id}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client disconnected: {client_id}")

    async def send_personal_message(self, message: dict, client_id: str):
        websocket = self.active_connections.get(client_id)
        if websocket:
            await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)

manager = ConnectionManager()
websocket_router = APIRouter()

@websocket_router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        await manager.send_personal_message({
            'status': 'connected',
            'message': 'Successfully connected to WhiteLabelRAG',
            'session_id': client_id
        }, client_id)
        while True:
            data = await websocket.receive_json()
            event = data.get('event')
            payload = data.get('data', {})
            if event == 'health_check':
                await manager.send_personal_message({
                    'status': 'healthy',
                    'timestamp': str(datetime.now())
                }, client_id)
            elif event == 'chat_message':
                message = payload.get('message', '')
                if not message.strip():
                    await manager.send_personal_message({
                        'text': 'Please enter a message.',
                        'error': True,
                        'timestamp': str(datetime.now())
                    }, client_id)
                    continue
                await manager.send_personal_message({
                    'status': 'processing',
                    'progress': 10,
                    'details': 'Processing your message...'
                }, client_id)
                try:
                    concierge = get_concierge_instance()
                    response = concierge.handle_message(message, client_id)
                    if not response or not isinstance(response, dict):
                        raise ValueError("Invalid response from Concierge")
                except Exception as e:
                    logger.error(f"Error in message processing: {str(e)}")
                    response = {
                        'text': 'I encountered an error while processing your message. Please try again.',
                        'error': True,
                        'timestamp': str(datetime.now())
                    }
                await manager.send_personal_message({
                    'text': response.get('text', 'No response generated.'),
                    'sources': response.get('sources', []),
                    'timestamp': response.get('timestamp', str(datetime.now())),
                    'session_id': client_id,
                    'error': response.get('error', False)
                }, client_id)
                status = 'error' if response.get('error') else 'completed'
                await manager.send_personal_message({
                    'status': status,
                    'progress': 100,
                    'details': 'Error processing message' if response.get('error') else 'Message processed successfully'
                }, client_id)
            else:
                await manager.send_personal_message({
                    'text': f'Unknown event: {event}',
                    'error': True,
                    'timestamp': str(datetime.now())
                }, client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"Critical error in WebSocket handler: {str(e)}")
        try:
            await manager.send_personal_message({
                'text': 'A critical error occurred. Please refresh the page and try again.',
                'error': True,
                'timestamp': str(datetime.now())
            }, client_id)
            await manager.send_personal_message({
                'status': 'error',
                'progress': 100,
                'details': 'Critical error occurred'
            }, client_id)
        except:
            logger.error("Failed to send error response")

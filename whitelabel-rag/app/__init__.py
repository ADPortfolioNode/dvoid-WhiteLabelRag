"""
WhiteLabelRAG Application Factory
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

# Initialize SocketIO
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25,
    logger=False,
    engineio_logger=False
)

def create_app(config_name=None):
    """Create and configure the Flask application."""
    
    app = Flask(__name__)
    
    # Load and validate configuration
    from app.config import Config
    try:
        Config.validate_config()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Tip: Set GEMINI_API_KEY as an environment variable or add it to your .env file")
        raise
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    # Ensure upload directory exists
    upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_path, exist_ok=True)
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {"origins": "*"},
        r"/socket.io/*": {"origins": "*"}
    })
    
    # Initialize SocketIO with app
    socketio.init_app(app)
    
    # Configure logging
    log_level = getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper())
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.main import main_bp
    app.register_blueprint(main_bp)
    
    # Register WebSocket events
    from app.websocket_events import register_websocket_events
    register_websocket_events(socketio)
    
    return app
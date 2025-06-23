r"""
WhiteLabelRAG Application Factory
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from app.websocket_events import websocket_router

def create_app():
    """Create and configure the FastAPI application."""  
      
    app = FastAPI()
    
    # Load and validate configuration
    from app.config import Config
    try:
        Config.validate_config()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("💡 Tip: Set GEMINI_API_KEY as an environment variable or add it to your .env file")
        raise
    
    # Configuration
    app.state.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.state.max_content_length = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    app.state.upload_folder = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    # Ensure upload directory exists
    upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), app.state.upload_folder)
    os.makedirs(upload_path, exist_ok=True)
    
    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Configure logging
    log_level = getattr(logging, os.environ.get('LOG_LEVEL', 'INFO').upper())
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Mount static files
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Setup templates
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    app.state.templates = Jinja2Templates(directory=templates_dir)
    
    # Register WebSocket router
    app.include_router(websocket_router)

    # Register API router
    from app.api.routes import api_router
    app.include_router(api_router, prefix="/api")

    from fastapi import APIRouter

    root_router = APIRouter()

    @root_router.get("/")
    async def root():
        return {"message": "Welcome to WhiteLabelRAG API. Please use the frontend UI to interact."}

    app.include_router(root_router)

    return app

"""
Configuration settings for WhiteLabelRAG
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'md', 'csv', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'mp3', 'wav', 'mp4', 'avi', 'mov'}
    
    # ChromaDB Configuration
    CHROMA_DB_PATH = os.environ.get('CHROMA_DB_PATH', './chromadb_data')
    
    # LLM Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # Internet Search API Configuration
    INTERNET_SEARCH_API_KEY = os.environ.get('INTERNET_SEARCH_API_KEY', '')
    INTERNET_SEARCH_ENGINE_ID = os.environ.get('INTERNET_SEARCH_ENGINE_ID', '')
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration."""
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Please set it as an environment variable or in your .env file."
            )
        return True
    
    # RAG Configuration
    CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', 500))
    CHUNK_OVERLAP = int(os.environ.get('CHUNK_OVERLAP', 50))
    TOP_K_RESULTS = int(os.environ.get('TOP_K_RESULTS', 3))
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Assistant Configuration
    ASSISTANT_CONFIGS = {
        'Concierge': {
            'name': 'Concierge',
            'task': 'general',
            'temperature': 0.2,
            'max_tokens': 1024,
            'system_prompt': 'You are the WhiteLabelRAG Concierge, an expert assistant that helps users find information and complete tasks.'
        },
        'SearchAgent': {
            'name': 'SearchAgent',
            'task': 'search',
            'temperature': 0.1,
            'max_tokens': 1024,
            'system_prompt': 'You are a search specialist that retrieves relevant document information from the knowledge base.'
        },
        'FileAgent': {
            'name': 'FileAgent',
            'task': 'fast',
            'temperature': 0.1,
            'max_tokens': 512,
            'system_prompt': 'You are a file processing specialist that handles document uploads and information extraction.'
        },
        'FunctionAgent': {
            'name': 'FunctionAgent',
            'task': 'fast',
            'temperature': 0.1,
            'max_tokens': 512,
            'system_prompt': 'You are a function execution specialist that runs operations safely based on user needs.'
        },
        'MultimediaAgent': {
            'name': 'MultimediaAgent',
            'task': 'fast',
            'temperature': 0.1,
            'max_tokens': 512,
            'system_prompt': 'You are a multimedia processing specialist that handles uploads, downloads, and processing of images, audio, and video files.'
        }
    }

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    FLASK_ENV = 'testing'
    CHROMA_DB_PATH = './test_chromadb_data'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

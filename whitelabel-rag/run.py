"""
WhiteLabelRAG Application Entry Point
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def check_environment():
    """Check if required environment variables are set."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable is not set!")
        print()
        print("🔧 How to fix this:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Set it as an environment variable:")
        print("   - Windows: set GEMINI_API_KEY=your_api_key_here")
        print("   - Linux/Mac: export GEMINI_API_KEY=your_api_key_here")
        print("3. Or add it to your .env file:")
        print("   - Copy .env.example to .env")
        print("   - Edit .env and add: GEMINI_API_KEY=your_api_key_here")
        print()
        return False
    
    print(f"✅ GEMINI_API_KEY is set (length: {len(api_key)} characters)")
    return True

def create_application():
    """Create application instance for Uvicorn."""
    if not check_environment():
        raise ValueError("Environment validation failed")
    
    from app import create_app
    return create_app()

app = create_application()

if __name__ == '__main__':
    print("🚀 Starting WhiteLabelRAG with FastAPI and Uvicorn...")
    print()
    
    if not check_environment():
        sys.exit(1)
    
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="debug" if debug else "info"
    )

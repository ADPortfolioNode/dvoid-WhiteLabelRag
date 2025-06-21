#!/usr/bin/env python3
"""
WhiteLabelRAG Application Entry Point
"""

import os
import sys

# Fix: Eventlet monkey patching must happen before any other imports
if os.environ.get("SOCKETIO_ASYNC_MODE", "eventlet") == "eventlet":
    import eventlet
    eventlet.monkey_patch()

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

# Create app instance for Gunicorn
def create_application():
    """Create application instance for Gunicorn."""
    if not check_environment():
        raise ValueError("Environment validation failed")
    
    from app import create_app
    return create_app()

# For Gunicorn
app = create_application()

@app.after_request
def add_header(response):
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    print("🚀 Starting WhiteLabelRAG...")
    print()
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    try:
        from app import socketio
        
        # Development server
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
        
        print(f"🌐 Starting server on http://localhost:{port}")
        print(f"🔧 Debug mode: {debug}")
        print("🛑 Press Ctrl+C to stop the server")
        print()
        
        # Add signal handling for graceful shutdown
        import signal
        
        def signal_handler(sig, frame):
            print("\n🛑 Shutting down gracefully...")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        socketio.run(
            app,
            host='127.0.0.1',
            port=port,
            debug=debug,
            use_reloader=False,
            log_output=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
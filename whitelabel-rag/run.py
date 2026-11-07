#!/usr/bin/env python3
"""
WhiteLabelRAG Application Entry Point
"""

# NOTE: no eventlet monkey patch here. The app's SocketIO runs in
# threading mode (see app/__init__.py) and production serves it with
# gunicorn's threaded worker. eventlet.monkey_patch() rewires the
# standard library for greenlets and deadlocks real threads, so it
# must not run in this process. (gunicorn 26 also removed the
# eventlet worker entirely, so --worker-class eventlet no longer
# exists; see docker-entrypoint.sh.)

import os
import sys
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
            log_output=True,
            # Werkzeug 3.x refuses to serve when stdin is not a TTY unless
            # this is set (same guard already fixed in run_stable.py).
            # Without it, `python run.py` fails to start at all when launched
            # backgrounded or from a non-terminal (e.g. an IDE run config).
            allow_unsafe_werkzeug=True
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
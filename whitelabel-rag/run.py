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
from flask import jsonify, render_template

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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/assistants')
def assistants():
    assistants = [
        {"name": "Concierge", "status": "online", "current_task": "Monitoring chat"},
        {"name": "SearchAgent", "status": "online", "current_task": None},
    ]
    return render_template('assistants.html', assistants=assistants)

@app.route('/health')
def health():
    assistants = [
        {"name": "Concierge", "status": "online", "current_task": "Monitoring chat"},
        {"name": "SearchAgent", "status": "online", "current_task": None},
    ]
    tasks = [
        {"id": 1, "description": "Summarize uploaded file", "progress": "complete"},
        {"id": 2, "description": "Answer user query", "progress": "in_progress"},
    ]
    endpoints = {
        "decompose": "/api/decompose",
        "query": "/api/query",
        "files": "/api/files"
    }
    return jsonify({
        "status": "ok",
        "assistants": assistants,
        "tasks": tasks,
        "endpoints": endpoints
    }), 200

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Prevent Flask app context conflicts in multi-process environments (Render/Gunicorn)
if __name__ == '__main__':
    print("🚀 Starting WhiteLabelRAG...")
    print()
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    try:
        from app import socketio
        
        # Use 0.0.0.0 for Render compatibility
        port = int(os.environ.get('PORT', 10000))  # Render sets PORT env var, default to 10000
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        print(f"🌐 Starting server on http://0.0.0.0:{port}")
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
        
        # Ensure only one app context per process
        if hasattr(app, 'app_context'):
            with app.app_context():
                socketio.run(
                    app,
                    host='0.0.0.0',  # Listen on all interfaces for Render
                    port=port,
                    debug=debug,
                    use_reloader=False,
                    log_output=True,
                    allow_unsafe_werkzeug=True
                )
        else:
            socketio.run(
                app,
                host='0.0.0.0',
                port=port,
                debug=debug,
                use_reloader=False,
                log_output=True,
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
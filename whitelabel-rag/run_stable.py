#!/usr/bin/env python3
"""
WhiteLabelRAG Stable Application Entry Point
Alternative runner with better threading and error handling
"""

import os
import sys
import signal
import threading
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

def run_server():
    """Run the server with better error handling."""
    try:
        from app import create_app, socketio
        app = create_app()
        
        # Development server configuration
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
        
        print(f"🌐 Starting server on http://localhost:{port}")
        print(f"🔧 Debug mode: {debug}")
        print("🛑 Press Ctrl+C to stop the server")
        print()
        
        # Use eventlet for better async handling if available
        try:
            import eventlet
            eventlet.monkey_patch()
            async_mode = 'eventlet'
            print("📡 Using eventlet for async operations")
        except ImportError:
            async_mode = 'threading'
            print("🧵 Using threading for async operations")
        
        # Reconfigure SocketIO with detected async mode
        socketio.async_mode = async_mode
        
        # Start the server
        socketio.run(
            app,
            host='127.0.0.1',
            port=port,
            debug=False,  # Disable debug to avoid reloader issues
            use_reloader=False,
            log_output=False
        )
        
    except Exception as e:
        print(f"❌ Server Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main entry point with signal handling."""
    print("🚀 Starting WhiteLabelRAG (Stable Mode)...")
    print()
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the server
    try:
        success = run_server()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
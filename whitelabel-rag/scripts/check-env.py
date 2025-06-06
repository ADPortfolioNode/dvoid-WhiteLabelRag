#!/usr/bin/env python3
"""
Environment variable checker for WhiteLabelRAG
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set."""
    print("🔍 Checking WhiteLabelRAG environment variables...")
    print()
    
    # Load .env file if it exists
    env_file_loaded = False
    if os.path.exists('.env'):
        load_dotenv()
        env_file_loaded = True
        print("✅ .env file found and loaded")
    else:
        print("⚠️ No .env file found")
    
    print()
    
    # Check required variables
    required_vars = {
        'GEMINI_API_KEY': 'Google Gemini API key for AI functionality'
    }
    
    optional_vars = {
        'FLASK_ENV': 'Flask environment (development/production)',
        'SECRET_KEY': 'Flask secret key for sessions',
        'CHROMA_DB_PATH': 'Path to ChromaDB data directory',
        'UPLOAD_FOLDER': 'Directory for uploaded files',
        'CHUNK_SIZE': 'Document chunk size for processing',
        'CHUNK_OVERLAP': 'Overlap between document chunks',
        'TOP_K_RESULTS': 'Number of top results to return'
    }
    
    all_good = True
    
    print("📋 Required Environment Variables:")
    print("-" * 50)
    
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'SECRET' in var:
                display_value = f"{'*' * (len(value) - 4)}{value[-4:]}" if len(value) > 4 else "****"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
            print(f"   {description}")
        else:
            print(f"❌ {var}: NOT SET")
            print(f"   {description}")
            all_good = False
        print()
    
    print("📋 Optional Environment Variables:")
    print("-" * 50)
    
    for var, description in optional_vars.items():
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚪ {var}: Using default")
        print(f"   {description}")
        print()
    
    if not all_good:
        print("❌ Missing required environment variables!")
        print()
        print("🔧 How to fix:")
        print("1. Get your Gemini API key from: https://makersuite.google.com/app/apikey")
        print("2. Set as environment variable:")
        print("   Windows: set GEMINI_API_KEY=your_api_key_here")
        print("   Linux/Mac: export GEMINI_API_KEY=your_api_key_here")
        print("3. Or add to .env file:")
        if not env_file_loaded:
            print("   - Copy .env.example to .env")
        print("   - Edit .env and add: GEMINI_API_KEY=your_api_key_here")
        print()
        return False
    
    print("✅ All required environment variables are set!")
    print("🚀 You're ready to run WhiteLabelRAG!")
    return True

if __name__ == '__main__':
    success = check_environment()
    sys.exit(0 if success else 1)
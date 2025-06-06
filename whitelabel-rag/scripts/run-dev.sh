#!/bin/bash

# Development server startup script

set -e

echo "🚀 Starting WhiteLabelRAG development server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check for GEMINI_API_KEY
if [ -z "$GEMINI_API_KEY" ]; then
    if [ ! -f ".env" ]; then
        echo "❌ GEMINI_API_KEY not set and .env file not found."
        echo ""
        echo "🔧 How to fix:"
        echo "1. Set environment variable: export GEMINI_API_KEY=your_api_key_here"
        echo "2. Or copy .env.example to .env and add your API key"
        echo "3. Get API key from: https://makersuite.google.com/app/apikey"
        exit 1
    fi
    echo "⚠️ GEMINI_API_KEY not set as environment variable, checking .env file..."
fi

# Set development environment
export FLASK_ENV=development
export FLASK_DEBUG=True

# Create directories if they don't exist
mkdir -p uploads chromadb_data logs

echo "✅ Environment ready"
echo "🌐 Starting server on http://localhost:5000"
echo "📝 Logs will be displayed below..."
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the application
python run.py
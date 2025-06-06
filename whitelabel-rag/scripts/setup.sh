#!/bin/bash

# WhiteLabelRAG Setup Script

set -e

echo "🚀 Setting up WhiteLabelRAG..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p chromadb_data
mkdir -p logs

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    
    echo "🔑 Generating secure SECRET_KEY..."
    GENERATED_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    echo "📝 Updating .env file with generated SECRET_KEY..."
    sed -i "s/SECRET_KEY=generate_with_python_secrets_token_urlsafe_32/SECRET_KEY=$GENERATED_SECRET/" .env
    
    echo ""
    echo "✅ Generated and set SECRET_KEY: $GENERATED_SECRET"
    echo ""
    echo "📝 IMPORTANT: You need to set your GEMINI_API_KEY!"
    echo ""
    echo "Option 1 - Set as environment variable:"
    echo "  export GEMINI_API_KEY=your_api_key_here"
    echo ""
    echo "Option 2 - Add to .env file:"
    echo "  Edit .env file and uncomment/set GEMINI_API_KEY=your_api_key_here"
    echo ""
    echo "Get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
fi

# Set permissions
echo "🔐 Setting permissions..."
chmod +x scripts/*.sh

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your GEMINI_API_KEY"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the application: python run.py"
echo "4. Open http://localhost:5000 in your browser"
echo ""
echo "For Docker deployment:"
echo "1. Set GEMINI_API_KEY in .env file"
echo "2. Run: docker-compose up -d"
#!/bin/bash

# Test runner script

set -e

echo "🧪 Running WhiteLabelRAG tests..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Install test dependencies if not already installed
pip install pytest pytest-flask pytest-cov

# Set test environment
export FLASK_ENV=testing

# Create test directories
mkdir -p test_uploads test_chromadb_data

# Run tests
echo "🔍 Running unit tests..."
pytest tests/ -v

# Run tests with coverage
echo "📊 Running tests with coverage..."
pytest --cov=app --cov-report=html --cov-report=term tests/

echo "✅ Tests completed!"
echo "📄 Coverage report generated in htmlcov/index.html"

# Cleanup test directories
rm -rf test_uploads test_chromadb_data
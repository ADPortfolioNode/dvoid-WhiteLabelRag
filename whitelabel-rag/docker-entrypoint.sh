#!/bin/bash
set -e

# WhiteLabelRAG Docker Entrypoint Script

echo "🚀 Starting WhiteLabelRAG..."

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    echo "⏳ Waiting for $service_name to be ready..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "✅ $service_name is ready!"
}

# Wait for Redis if configured
if [ -n "$REDIS_URL" ]; then
    REDIS_HOST=$(echo $REDIS_URL | cut -d'/' -f3 | cut -d':' -f1)
    REDIS_PORT=$(echo $REDIS_URL | cut -d'/' -f3 | cut -d':' -f2)
    wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
fi

# Validate required environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY environment variable is required"
    exit 1
fi

# Generate SECRET_KEY if not provided
if [ -z "$SECRET_KEY" ]; then
    echo "🔑 Generating SECRET_KEY..."
    export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /app/uploads /app/chromadb_data /app/logs

# Set proper permissions
chmod 755 /app/uploads /app/chromadb_data /app/logs

# Run database migrations or setup if needed
echo "🔧 Running setup tasks..."

# Validate environment
echo "✅ Validating environment..."
python -c "
import os
from app.config import Config
try:
    Config.validate_config()
    print('✅ Configuration is valid')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    exit(1)
"

# Start the application based on environment
if [ "$FLASK_ENV" = "development" ]; then
    echo "🔧 Starting in development mode..."
    exec python run.py
else
    echo "🚀 Starting in production mode with Gunicorn..."
    
    # Default values
    WORKERS=${WORKERS:-4}
    TIMEOUT=${TIMEOUT:-120}
    KEEPALIVE=${KEEPALIVE:-2}
    BIND=${BIND:-0.0.0.0:5000}
    
    exec gunicorn \
        --bind "$BIND" \
        --workers "$WORKERS" \
        --timeout "$TIMEOUT" \
        --keep-alive "$KEEPALIVE" \
        --worker-class eventlet \
        --worker-connections 1000 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --preload \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        "run:app"
fi
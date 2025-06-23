#!/bin/bash
set -e

# Print environment info
echo "Starting PocketPro:SBA Edition..."
echo "PORT: ${PORT:-10000}"
echo "FLASK_ENV: ${FLASK_ENV:-production}"

# Check for required environment variables
if [ -z "${GEMINI_API_KEY}" ]; then
    echo "ERROR: GEMINI_API_KEY environment variable is required"
    exit 1
fi

# Create a random SECRET_KEY if not provided
if [ -z "${SECRET_KEY}" ]; then
    export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "Generated random SECRET_KEY"
fi

# Create necessary directories
mkdir -p uploads chromadb_data logs

# Wait for Redis to be ready if it's available
if nc -z redis 6379 2>/dev/null; then
    echo "Waiting for Redis..."
    until nc -z redis 6379; do
        sleep 1
    done
    echo "Redis is available"
fi

# Run health check
echo "Running initial health check..."
python -c "import sys; sys.path.append('/app'); from app.utils.health_check import run_health_check; run_health_check()"

# Execute the command
exec "$@"

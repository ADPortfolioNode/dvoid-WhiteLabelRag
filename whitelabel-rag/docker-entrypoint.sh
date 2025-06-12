#!/bin/bash
set -e

# WhiteLabelRAG Docker Entrypoint Script

# Environment variable for status message visibility (default: true)
SHOW_STATUS_MESSAGES="${SHOW_STATUS_MESSAGES:-true}"
# Environment variable for service wait timeout in seconds (default: 5 seconds)
SERVICE_WAIT_TIMEOUT="${SERVICE_WAIT_TIMEOUT:-5}"
# Environment variable for Docker lifecycle management (default: "run")
# Possible values: "run", "shutdown", "rebuild", "restart"
DOCKER_ACTION="${DOCKER_ACTION:-run}"

# Docker lifecycle management function
manage_docker() {
    local action=$1
    
    case "$action" in
        shutdown)
            if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
                echo "🛑 Shutting down Docker containers..."
            fi
            docker-compose down
            exit 0
            ;;
        rebuild)
            if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
                echo "🔄 Rebuilding Docker image..."
            fi
            docker-compose down
            docker-compose build
            docker-compose up -d
            exit 0
            ;;
        restart)
            if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
                echo "🔄 Restarting Docker containers..."
            fi
            docker-compose restart
            exit 0
            ;;
        run)
            if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
                echo "🚀 Starting WhiteLabelRAG..."
            fi
            # Continue with normal startup
            ;;
        *)
            echo "❌ Error: Unknown DOCKER_ACTION value: $action. Valid values are: run, shutdown, rebuild, restart"
            exit 1
            ;;
    esac
}

# Handle Docker lifecycle actions if specified
manage_docker "$DOCKER_ACTION"

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout=${SERVICE_WAIT_TIMEOUT} # Use the already defaulted variable
    local elapsed_time=0
    local sleep_interval=1
    local printed_dots=false

    if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
        echo "⏳ Waiting for $service_name at $host:$port (timeout: ${timeout}s)..."
    fi

    while ! nc -z "$host" "$port"; do
        if [ "$elapsed_time" -ge "$timeout" ]; then
            if [ "$SHOW_STATUS_MESSAGES" = "true" ] && [ "$printed_dots" = "true" ]; then
                echo # Newline if dots were printed before timeout message
            fi
            echo "❌ Error: Timed out waiting for $service_name at $host:$port after ${timeout}s."
            exit 1
        fi
        sleep "$sleep_interval"
        elapsed_time=$((elapsed_time + sleep_interval))
        if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
            echo -n "."
            printed_dots=true
        fi
    done
    
    if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
        if [ "$printed_dots" = "true" ]; then
            echo # Newline after dots
        fi
        echo "✅ $service_name is ready!"
    fi
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
    if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
        echo "🔑 Generating SECRET_KEY..."
    fi
    export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
fi

# Create necessary directories
if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
    echo "📁 Creating directories..."
fi
mkdir -p /app/uploads /app/chromadb_data /app/logs

# Set proper permissions
chmod 755 /app/uploads /app/chromadb_data /app/logs

# Run database migrations or setup if needed
if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
    echo "🔧 Running setup tasks..."
fi

# Validate environment
if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
    echo "✅ Validating environment..."
fi
python -c "
import os
import sys
from app.config import Config

# Terminal colors - using minimal styling that works in most terminals
# Black text on white background is default, using dim grey for subtle emphasis
RESET = '\033[0m'
GREY = '\033[2m'  # Dim/faint text (light grey)
ERROR = '\033[31m'  # Red for errors (standard)

try:
    Config.validate_config()
    # Only print success if SHOW_STATUS_MESSAGES is true (case-insensitive)
    if os.environ.get('SHOW_STATUS_MESSAGES', 'true').lower() == 'true':
        print(f'✅ {GREY}Configuration is valid{RESET}')
except Exception as e:
    error_message = str(e)
    print(f'{ERROR}❌ Configuration error: {error_message}{RESET}', file=sys.stderr)
    sys.exit(1)
"

# Start the application based on environment
if [ "$FLASK_ENV" = "development" ]; then
    if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
        echo "🔧 Starting in development mode..."
    fi
    exec python run.py
else
    if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
        echo "🚀 Starting in production mode with Gunicorn..."
    fi
    
    # Default values
    WORKERS=${WORKERS:-4}
    TIMEOUT=${TIMEOUT:-120}
    KEEPALIVE=${KEEPALIVE:-2}
    BIND=${BIND:-0.0.0.0:5000}
    
    if [ "$1" = 'gunicorn' ]; then
        if [ "$SHOW_STATUS_MESSAGES" = "true" ]; then
            echo "🦄 Starting Gunicorn..."
            echo "🔧 Workers: ${WORKERS:-4}"
            echo "⏱️ Timeout: ${TIMEOUT:-120}"
            echo "🔗 Keep-Alive: ${KEEPALIVE:-2}"
            echo "🌐 Listening on: 0.0.0.0:5000"
        fi
        # Ensure Flask app environment variables are set correctly for Gunicorn
        export FLASK_APP="run:app" # Explicitly set the correct application module and variable
        export FLASK_ENV=${FLASK_ENV:-production}

        # Start Gunicorn with eventlet worker
        exec gunicorn \
            --workers "$WORKERS" \
            --timeout "$TIMEOUT" \
            --keep-alive "$KEEPALIVE" \
            --bind "$BIND" \
            --worker-class eventlet \
            "$FLASK_APP"
    fi
fi
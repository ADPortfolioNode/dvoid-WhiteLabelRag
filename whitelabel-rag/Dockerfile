# WhiteLabelRAG Production Dockerfile
FROM python:3.11-slim

# Set metadata
LABEL maintainer="WhiteLabelRAG Team"
LABEL description="Production-ready WhiteLabelRAG application"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn eventlet

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p uploads chromadb_data logs \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV WORKERS=4
ENV TIMEOUT=120
ENV KEEPALIVE=2

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Switch to non-root user
USER appuser

# Set entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]

# Default command
CMD ["gunicorn"]
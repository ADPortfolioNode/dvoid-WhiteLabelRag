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
# Ensure the app runs on the port Render expects (default 10000 if set, else 5000)
ENV PORT=10000

# Expose the correct port for Render.com (Render sets $PORT)
EXPOSE 10000

# Set entrypoint and default command to use the PORT env variable
ENTRYPOINT ["gunicorn"]
CMD ["-b", "0.0.0.0:10000", "-k", "eventlet", "run:app"]

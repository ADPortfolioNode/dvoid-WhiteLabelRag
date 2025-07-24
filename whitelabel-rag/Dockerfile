
# Multi-stage build for production-ready WhiteLabelRAG Docker image

# Builder stage: install dependencies and build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Python builder stage
FROM python:3.12-slim AS python-builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y gcc g++ curl git netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python dependencies to a separate directory
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn eventlet

# Final stage: minimal runtime image
FROM python:3.12-slim

WORKDIR /app

# Install netcat and curl for runtime and healthcheck
RUN apt-get update && apt-get install -y netcat-openbsd curl && rm -rf /var/lib/apt/lists/*

# Copy installed python packages from python builder
COPY --from=python-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=python-builder /usr/local/bin /usr/local/bin

# Copy frontend build files from frontend-builder
COPY --from=frontend-builder /app/frontend/build /app/static/frontend

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p uploads chromadb_data logs \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app

# Set environment variables
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV WORKERS=4
ENV TIMEOUT=120
ENV KEEPALIVE=2
ENV PORT=${PORT:-10000}
ENV CHROMA_SERVER_HOST=chroma
ENV CHROMA_SERVER_HTTP_PORT=8000

# Expose the port dynamically
EXPOSE ${PORT:-10000}

# Copy entrypoint script to /usr/local/bin and set permissions as root
RUN cp /app/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh \
    && chmod +x /usr/local/bin/docker-entrypoint.sh

# Switch to non-root user after setting permissions
USER appuser

# Use entrypoint script
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Use gunicorn as the command with dynamic port binding
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "4"]

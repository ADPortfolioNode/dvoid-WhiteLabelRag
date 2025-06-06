# WhiteLabelRAG Docker Deployment Guide

This guide covers all Docker deployment scenarios for WhiteLabelRAG, from development to production.

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd whitelabel-rag

# Create environment file
cp .env.example .env

# Edit .env and add your API key
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Production Deployment
```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f whitelabel-rag
```

### 3. Access the Application
- **Web Interface**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

## 📋 Deployment Options

### Option 1: Production with Docker Compose (Recommended)

**Features:**
- Production-ready Gunicorn server
- Redis for session storage
- Named volumes for data persistence
- Health checks and auto-restart
- Logging configuration

```bash
# Start production stack
docker-compose up -d

# Scale the application (if needed)
docker-compose up -d --scale whitelabel-rag=3

# Stop services
docker-compose down

# Stop and remove volumes (⚠️ Data loss)
docker-compose down -v
```

### Option 2: Development with Live Reload

**Features:**
- Development server with debug mode
- Live code reloading
- Development tools included
- Separate development volumes

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Access container for debugging
docker-compose -f docker-compose.dev.yml exec whitelabel-rag-dev bash
```

### Option 3: Production with Nginx Reverse Proxy

**Features:**
- Nginx reverse proxy with SSL support
- Rate limiting and caching
- Load balancing ready
- Security headers

```bash
# Start with Nginx proxy
docker-compose --profile nginx up -d

# Access via Nginx
# HTTP: http://localhost
# HTTPS: https://localhost (after SSL setup)
```

### Option 4: Single Container Deployment

```bash
# Build the image
docker build -t whitelabel-rag .

# Run single container
docker run -d \
  --name whitelabel-rag \
  -p 5000:5000 \
  -e GEMINI_API_KEY=your_api_key_here \
  -v whitelabel_uploads:/app/uploads \
  -v whitelabel_chromadb:/app/chromadb_data \
  -v whitelabel_logs:/app/logs \
  whitelabel-rag
```

## ⚙️ Configuration

### Environment Variables

**Required:**
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

**Optional:**
```bash
# Application
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
LOG_LEVEL=INFO

# Server Configuration
PORT=5000
WORKERS=4
TIMEOUT=120
KEEPALIVE=2

# Database
REDIS_URL=redis://redis:6379/0

# File Storage
UPLOAD_FOLDER=/app/uploads
CHROMA_DB_PATH=/app/chromadb_data
```

### Docker Compose Override

Create `docker-compose.override.yml` for local customizations:

```yaml
version: '3.8'

services:
  whitelabel-rag:
    environment:
      - LOG_LEVEL=DEBUG
    ports:
      - "5001:5000"  # Use different port
```

## 🔧 Advanced Configuration

### Custom Nginx Configuration

1. **Create custom nginx.conf:**
```bash
mkdir -p nginx/ssl
# Copy your SSL certificates to nginx/ssl/
```

2. **Update nginx.conf for your domain:**
```nginx
server_name your-domain.com;
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

3. **Enable HTTPS:**
```bash
# Uncomment HTTPS server block in nginx/nginx.conf
docker-compose --profile nginx up -d
```

### Scaling and Load Balancing

```bash
# Scale application containers
docker-compose up -d --scale whitelabel-rag=3

# Nginx will automatically load balance
```

### Persistent Data Management

```bash
# Backup data
docker run --rm -v whitelabel-rag_chromadb_data:/data -v $(pwd):/backup alpine tar czf /backup/chromadb_backup.tar.gz -C /data .

# Restore data
docker run --rm -v whitelabel-rag_chromadb_data:/data -v $(pwd):/backup alpine tar xzf /backup/chromadb_backup.tar.gz -C /data
```

## 🔍 Monitoring and Maintenance

### Health Checks

```bash
# Check application health
curl http://localhost:5000/health

# Check container health
docker-compose ps
```

### Logs Management

```bash
# View application logs
docker-compose logs -f whitelabel-rag

# View all service logs
docker-compose logs -f

# View logs with timestamps
docker-compose logs -f -t

# Limit log output
docker-compose logs --tail=100 -f whitelabel-rag
```

### Container Management

```bash
# Restart services
docker-compose restart

# Update containers
docker-compose pull
docker-compose up -d

# Clean up
docker system prune -f
docker volume prune -f
```

## 🐛 Troubleshooting

### Common Issues

**1. Container won't start:**
```bash
# Check logs
docker-compose logs whitelabel-rag

# Check environment variables
docker-compose config
```

**2. API key issues:**
```bash
# Verify environment file
cat .env

# Check container environment
docker-compose exec whitelabel-rag env | grep GEMINI
```

**3. Port conflicts:**
```bash
# Check what's using the port
netstat -tulpn | grep :5000

# Use different port
PORT=5001 docker-compose up -d
```

**4. Volume permission issues:**
```bash
# Fix permissions
docker-compose exec whitelabel-rag chown -R appuser:appuser /app/uploads
```

### Debug Mode

```bash
# Run in debug mode
docker-compose -f docker-compose.dev.yml up -d

# Access container shell
docker-compose exec whitelabel-rag-dev bash

# Run tests inside container
docker-compose exec whitelabel-rag-dev python -m pytest
```

## 🚀 Production Deployment Checklist

### Pre-deployment
- [ ] Set strong `SECRET_KEY`
- [ ] Configure proper `GEMINI_API_KEY`
- [ ] Set up SSL certificates (for HTTPS)
- [ ] Configure domain name
- [ ] Set up monitoring
- [ ] Plan backup strategy

### Security
- [ ] Use non-root user (✅ included)
- [ ] Enable HTTPS with valid certificates
- [ ] Configure rate limiting (✅ included in Nginx)
- [ ] Set up firewall rules
- [ ] Regular security updates

### Performance
- [ ] Tune worker count based on CPU cores
- [ ] Configure Redis for session storage
- [ ] Set up log rotation
- [ ] Monitor resource usage
- [ ] Configure caching headers

### Monitoring
- [ ] Set up health check monitoring
- [ ] Configure log aggregation
- [ ] Set up alerting
- [ ] Monitor disk usage for volumes
- [ ] Track application metrics

## 📊 Performance Tuning

### Worker Configuration
```bash
# For CPU-intensive workloads
WORKERS=4  # Number of CPU cores

# For I/O-intensive workloads
WORKERS=8  # 2x CPU cores
```

### Memory Optimization
```bash
# Limit container memory
docker-compose up -d --memory=2g
```

### Database Optimization
```bash
# Redis memory optimization
docker-compose exec redis redis-cli CONFIG SET maxmemory 256mb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy WhiteLabelRAG

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          docker-compose pull
          docker-compose up -d
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

### Docker Registry
```bash
# Build and tag
docker build -t your-registry/whitelabel-rag:latest .

# Push to registry
docker push your-registry/whitelabel-rag:latest

# Deploy from registry
docker run -d your-registry/whitelabel-rag:latest
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Gunicorn Documentation](https://gunicorn.org/)

---

## 🎉 Success!

Your WhiteLabelRAG application is now running in Docker! 

- **Development**: Use `docker-compose.dev.yml` for development
- **Production**: Use `docker-compose.yml` for production
- **With Proxy**: Add `--profile nginx` for reverse proxy

For support, check the logs and troubleshooting section above.
# WhiteLabelRAG Deployment Guide

## Deployment Options

### 1. Local Development

**Quick Start:**
```bash
# Setup
python scripts/setup.sh  # Linux/Mac
scripts\setup.bat        # Windows

# Configure API keys
export GEMINI_API_KEY=your_api_key_here
export GOOGLE_API_KEY=your_google_api_key_here  # For internet search (optional)
export INTERNET_SEARCH_ENGINE_ID=your_search_engine_id_here  # For internet search (optional)

# Run
python run.py
```

**Access:** http://localhost:5000

### 2. Docker Deployment (Recommended)

**Prerequisites:**
- Docker and Docker Compose installed
- GEMINI_API_KEY environment variable set
- GOOGLE_API_KEY environment variable set (optional for internet search)
- INTERNET_SEARCH_ENGINE_ID environment variable set (optional for internet search)

**Single Container:**
```bash
# Set API keys
export GEMINI_API_KEY=your_api_key_here
export GOOGLE_API_KEY=your_google_api_key_here  # Optional
export INTERNET_SEARCH_ENGINE_ID=your_search_engine_id_here  # Optional

# Build and run
docker build -t whitelabel-rag .
docker run -p 5000:5000 -e GEMINI_API_KEY=$GEMINI_API_KEY whitelabel-rag
```

**Docker Compose (Recommended):**
```bash
# Create .env file with all required API keys
cat > .env << EOL
GEMINI_API_KEY=your_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
INTERNET_SEARCH_ENGINE_ID=your_search_engine_id_here
EOL

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Access:** http://localhost:5000

### 3. Production Deployment

#### Option A: VPS/Cloud Server

**1. Server Setup (Ubuntu/Debian):**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx git

# Create user
sudo useradd -m -s /bin/bash whitelabelrag
sudo usermod -aG sudo whitelabelrag
```

**2. Application Setup:**
```bash
# Switch to app user
sudo su - whitelabelrag

# Clone repository
git clone <your-repo-url> whitelabel-rag
cd whitelabel-rag

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your GEMINI_API_KEY

# Test installation
python scripts/test-setup.py
```

**3. Systemd Service:**
```bash
# Create service file
sudo nano /etc/systemd/system/whitelabel-rag.service
```

```ini
[Unit]
Description=WhiteLabelRAG Application
After=network.target

[Service]
Type=simple
User=whitelabelrag
WorkingDirectory=/home/whitelabelrag/whitelabel-rag
Environment=PATH=/home/whitelabelrag/whitelabel-rag/venv/bin
ExecStart=/home/whitelabelrag/whitelabel-rag/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable whitelabel-rag
sudo systemctl start whitelabel-rag

# Check status
sudo systemctl status whitelabel-rag
```

**4. Nginx Configuration:**
```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/whitelabel-rag
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 16M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/whitelabel-rag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**5. SSL with Let's Encrypt:**
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Option B: Cloud Platforms

**Heroku:**
```bash
# Install Heroku CLI
# Create Procfile
echo "web: python run.py" > Procfile

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set GEMINI_API_KEY=your_api_key_here

# Deploy
git push heroku main
```

**AWS EC2:**
```bash
# Launch EC2 instance (Ubuntu 20.04+)
# Follow VPS setup instructions above
# Configure security groups for ports 80, 443, 22
```

**Google Cloud Platform:**
```bash
# Use Cloud Run for serverless deployment
# Create Dockerfile (already provided)
# Deploy with gcloud CLI
gcloud run deploy whitelabel-rag --source .
```

**DigitalOcean:**
```bash
# Create droplet
# Follow VPS setup instructions
# Use DigitalOcean App Platform for easier deployment
```

### 4. Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: whitelabel-rag
spec:
  replicas: 2
  selector:
    matchLabels:
      app: whitelabel-rag
  template:
    metadata:
      labels:
        app: whitelabel-rag
    spec:
      containers:
      - name: whitelabel-rag
        image: whitelabel-rag:latest
        ports:
        - containerPort: 5000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: whitelabel-rag-secrets
              key: gemini-api-key
        volumeMounts:
        - name: uploads
          mountPath: /app/uploads
        - name: chromadb
          mountPath: /app/chromadb_data
      volumes:
      - name: uploads
        persistentVolumeClaim:
          claimName: uploads-pvc
      - name: chromadb
        persistentVolumeClaim:
          claimName: chromadb-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: whitelabel-rag-service
spec:
  selector:
    app: whitelabel-rag
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

## Environment Configuration

### Production Environment Variables

```bash
# Required
GEMINI_API_KEY=your_production_api_key

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your_strong_secret_key_here
FLASK_DEBUG=False

# Database
CHROMA_DB_PATH=/app/data/chromadb
UPLOAD_FOLDER=/app/data/uploads

# Performance
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=3

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# Security
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### Security Configuration

**1. Generate Strong Secret Key:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

**2. Environment Security:**
```bash
# Set restrictive permissions on .env
chmod 600 .env

# Use environment variables in production
export GEMINI_API_KEY=your_key
export SECRET_KEY=your_secret
```

**3. Firewall Configuration:**
```bash
# Ubuntu/Debian
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## Monitoring and Maintenance

### Health Checks

**Application Health:**
```bash
# Built-in health check
curl http://localhost:5000/health

# Comprehensive health check
python scripts/health-check.py
```

**System Monitoring:**
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor resources
htop
df -h
free -h
```

### Logging

**Application Logs:**
```bash
# View logs
tail -f logs/app.log

# Systemd logs
sudo journalctl -u whitelabel-rag -f

# Docker logs
docker-compose logs -f
```

**Log Rotation:**
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/whitelabel-rag
```

```
/home/whitelabelrag/whitelabel-rag/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 whitelabelrag whitelabelrag
    postrotate
        systemctl reload whitelabel-rag
    endscript
}
```

### Backup Strategy

**Automated Backup Script:**
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/whitelabel-rag"
APP_DIR="/home/whitelabelrag/whitelabel-rag"

mkdir -p $BACKUP_DIR

# Backup uploads and ChromaDB
tar -czf $BACKUP_DIR/data_$DATE.tar.gz \
    $APP_DIR/uploads \
    $APP_DIR/chromadb_data

# Backup configuration
cp $APP_DIR/.env $BACKUP_DIR/env_$DATE

# Keep only last 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "env_*" -mtime +7 -delete
```

**Cron Job:**
```bash
# Add to crontab
0 2 * * * /home/whitelabelrag/backup.sh
```

### Updates and Maintenance

**Application Updates:**
```bash
# Backup first
./backup.sh

# Pull updates
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart whitelabel-rag

# Verify
python scripts/health-check.py
```

**System Updates:**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Restart if kernel updated
sudo reboot
```

## Performance Optimization

### Application Tuning

**1. Gunicorn for Production:**
```bash
# Install Gunicorn
pip install gunicorn

# Create gunicorn config
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "eventlet"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
```

**2. Update systemd service:**
```ini
ExecStart=/home/whitelabelrag/whitelabel-rag/venv/bin/gunicorn -c gunicorn.conf.py run:app
```

### Database Optimization

**ChromaDB Tuning:**
```python
# In chroma_service.py
settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=chroma_path,
    anonymized_telemetry=False,
    allow_reset=True
)
```

### Caching

**Redis for Session Storage:**
```bash
# Install Redis
sudo apt install -y redis-server

# Configure in .env
REDIS_URL=redis://localhost:6379/0
```

## Scaling

### Horizontal Scaling

**Load Balancer (Nginx):**
```nginx
upstream whitelabel_rag {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    location / {
        proxy_pass http://whitelabel_rag;
    }
}
```

**Multiple Instances:**
```bash
# Run multiple instances on different ports
PORT=5000 python run.py &
PORT=5001 python run.py &
PORT=5002 python run.py &
```

### Vertical Scaling

**Resource Allocation:**
- **CPU**: 2-4 cores minimum
- **RAM**: 4-8GB minimum (more for large document collections)
- **Storage**: SSD recommended, 50GB+ for production
- **Network**: 1Gbps for good performance

## Troubleshooting Deployment

### Common Issues

**1. Permission Errors:**
```bash
# Fix ownership
sudo chown -R whitelabelrag:whitelabelrag /home/whitelabelrag/whitelabel-rag

# Fix permissions
chmod +x scripts/*.sh
chmod 600 .env
```

**2. Port Conflicts:**
```bash
# Check what's using port 5000
sudo netstat -tulpn | grep :5000

# Kill process if needed
sudo kill -9 <PID>
```

**3. Memory Issues:**
```bash
# Check memory usage
free -h

# Add swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**4. SSL Certificate Issues:**
```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

### Monitoring Commands

```bash
# Check service status
sudo systemctl status whitelabel-rag

# Check application health
curl -f http://localhost:5000/health

# Check logs
sudo journalctl -u whitelabel-rag --since "1 hour ago"

# Check resource usage
htop
df -h
free -h
```

## Security Checklist

- [ ] GEMINI_API_KEY stored securely
- [ ] Strong SECRET_KEY generated
- [ ] HTTPS enabled with valid certificate
- [ ] Firewall configured properly
- [ ] Regular security updates applied
- [ ] File upload validation enabled
- [ ] Rate limiting implemented
- [ ] Logs monitored for suspicious activity
- [ ] Backup strategy in place
- [ ] Access logs reviewed regularly
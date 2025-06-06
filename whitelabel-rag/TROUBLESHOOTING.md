# WhiteLabelRAG Troubleshooting Guide

## Quick Diagnostics

### 🔧 Run Diagnostic Scripts

```bash
# Check environment and setup
python scripts/check-env.py

# Test installation
python scripts/test-setup.py

# Health check (server must be running)
python scripts/health-check.py

# Run demo
python scripts/demo.py
```

## Common Issues

### 1. GEMINI_API_KEY Not Set

**Error Messages:**
- "GEMINI_API_KEY environment variable is required"
- "GEMINI_API_KEY not found in environment variables"

**Solutions:**

**Option A: Environment Variable**
```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

**Option B: .env File**
```bash
# Copy example file
cp .env.example .env

# Edit .env and add:
GEMINI_API_KEY=your_api_key_here
```

**Get API Key:** https://makersuite.google.com/app/apikey

### 2. Module Import Errors

**Error Messages:**
- "ModuleNotFoundError: No module named 'flask'"
- "ImportError: cannot import name..."

**Solutions:**
```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Port Already in Use

**Error Messages:**
- "Address already in use"
- "Port 5000 is already in use"

**Solutions:**
```bash
# Find process using port 5000
# Windows:
netstat -ano | findstr :5000

# Linux/Mac:
lsof -i :5000

# Kill the process or change port in run.py
```

### 4. ChromaDB Issues

**Error Messages:**
- "ChromaDB connection failed"
- "Database is locked"
- "Permission denied"

**Solutions:**
```bash
# Delete and recreate ChromaDB data
rm -rf chromadb_data
mkdir chromadb_data

# Check permissions
chmod 755 chromadb_data

# On Windows, run as administrator if needed
```

### 5. File Upload Failures

**Error Messages:**
- "File too large"
- "File type not supported"
- "Upload failed"

**Solutions:**
- Check file size (max 16MB)
- Verify file format (PDF, DOCX, TXT, MD, CSV)
- Ensure uploads directory exists and is writable
- Check disk space

### 6. WebSocket Connection Issues

**Error Messages:**
- "WebSocket connection failed"
- "Real-time updates not working"

**Solutions:**
```bash
# Check if Flask-SocketIO is installed
pip install flask-socketio

# Try different transport methods in browser console:
# socket.io.opts.transports = ['polling']
```

### 7. Memory Issues

**Error Messages:**
- "Out of memory"
- "Process killed"

**Solutions:**
- Reduce chunk size in configuration
- Process smaller documents
- Increase system RAM
- Use external ChromaDB instance

### 8. API Rate Limits

**Error Messages:**
- "Rate limit exceeded"
- "API quota exceeded"

**Solutions:**
- Check Gemini API usage in Google Cloud Console
- Implement request throttling
- Cache responses
- Upgrade API plan if needed

## Performance Issues

### Slow Document Processing

**Causes:**
- Large documents
- Limited system resources
- Network latency

**Solutions:**
```bash
# Optimize chunk size
CHUNK_SIZE=300
CHUNK_OVERLAP=30

# Use faster embedding model
# Edit chroma_service.py to use sentence-transformers
```

### Slow Search Responses

**Causes:**
- Large vector database
- Complex queries
- Network issues

**Solutions:**
- Reduce TOP_K_RESULTS
- Use basic RAG workflow for simple queries
- Optimize ChromaDB configuration

## Development Issues

### Hot Reload Not Working

**Solutions:**
```bash
# Ensure debug mode is enabled
export FLASK_DEBUG=True

# Or set in .env file
FLASK_DEBUG=True
```

### Static Files Not Loading

**Solutions:**
- Check file paths in templates
- Clear browser cache
- Verify static directory structure

### Database Schema Issues

**Solutions:**
```bash
# Reset ChromaDB
rm -rf chromadb_data
python run.py  # Will recreate database
```

## Production Deployment Issues

### Docker Build Failures

**Solutions:**
```bash
# Check Dockerfile syntax
docker build --no-cache -t whitelabel-rag .

# Check system resources
docker system df
docker system prune
```

### Environment Variables in Docker

**Solutions:**
```bash
# Ensure .env file exists
cp .env.example .env

# Or set directly in docker-compose.yml
environment:
  - GEMINI_API_KEY=your_key_here
```

### SSL/HTTPS Issues

**Solutions:**
- Use reverse proxy (Nginx)
- Configure SSL certificates
- Update CORS settings for HTTPS

## Logging and Debugging

### Enable Debug Logging

```bash
# Set in .env file
LOG_LEVEL=DEBUG
FLASK_DEBUG=True

# Or environment variable
export LOG_LEVEL=DEBUG
```

### Check Application Logs

```bash
# View logs
tail -f logs/app.log

# Or check console output when running
python run.py
```

### Browser Developer Tools

1. Open browser developer tools (F12)
2. Check Console tab for JavaScript errors
3. Check Network tab for failed requests
4. Check WebSocket connections

## Getting Help

### Diagnostic Information

When reporting issues, include:

```bash
# System information
python --version
pip list | grep -E "(flask|chroma|google)"

# Environment check
python scripts/check-env.py

# Setup test
python scripts/test-setup.py

# Health check (if server running)
python scripts/health-check.py
```

### Log Files

Include relevant log files:
- Application logs: `logs/app.log`
- Console output from `python run.py`
- Browser console errors

### Configuration

Include (with sensitive data removed):
- `.env` file contents
- System specifications
- Docker version (if using Docker)

## Advanced Troubleshooting

### Memory Profiling

```python
# Add to run.py for memory profiling
import tracemalloc
tracemalloc.start()

# Your code here

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
```

### Performance Profiling

```python
# Add to routes for performance profiling
import cProfile
import pstats

def profile_route():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your route code here
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

### Database Debugging

```python
# Check ChromaDB collection status
from app.services.chroma_service import get_chroma_service_instance

chroma = get_chroma_service_instance()
stats = chroma.get_collection_stats()
print(f"Documents: {stats['documents_count']}")
print(f"Steps: {stats['steps_count']}")
```

## Prevention

### Regular Maintenance

1. **Update Dependencies**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

2. **Clean Up Data**
   ```bash
   # Remove old uploads
   find uploads -type f -mtime +30 -delete
   
   # Clean ChromaDB if needed
   # (Be careful - this removes all indexed documents)
   ```

3. **Monitor Resources**
   - Check disk space regularly
   - Monitor memory usage
   - Watch API usage quotas

4. **Backup Important Data**
   ```bash
   # Backup uploads and ChromaDB
   tar -czf backup_$(date +%Y%m%d).tar.gz uploads chromadb_data
   ```

### Best Practices

1. **Environment Management**
   - Use virtual environments
   - Pin dependency versions
   - Keep .env files secure

2. **Resource Management**
   - Set appropriate chunk sizes
   - Limit file upload sizes
   - Monitor API usage

3. **Error Handling**
   - Check logs regularly
   - Implement proper error handling
   - Use health checks

4. **Security**
   - Keep API keys secure
   - Use HTTPS in production
   - Validate all inputs
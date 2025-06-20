# WhiteLabelRAG Quick Start Guide

## Prerequisites

1. **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
2. **Google Gemini API Key** - [Get API Key](https://makersuite.google.com/app/apikey)
3. **Google API Key** (optional, for internet search) - [Get API Key](https://console.cloud.google.com/)
4. **Git** (optional) - [Download Git](https://git-scm.com/downloads)

## 🚀 Quick Setup (5 minutes)

### Option 1: Automated Setup

**Windows:**
```cmd
# Run the setup script
scripts\setup.bat

# Edit .env file and add your API keys
notepad .env

# Start the development server
scripts\run-dev.bat
```

**Linux/Mac:**
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run the setup script
./scripts/setup.sh

# Edit .env file and add your API keys
nano .env

# Start the development server
./scripts/run-dev.sh
```

### Optional: Set Up Internet Search

For internet search capability:

1. Set up a Google Custom Search Engine - [Instructions](GOOGLE_SEARCH_SETUP.md)
2. Add to your `.env` file:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   INTERNET_SEARCH_ENGINE_ID=your_search_engine_id_here
   ```
3. Test the configuration:
   ```
   # Windows
   scripts\test_google_search.bat
   
   # Linux/Mac
   ./scripts/test_google_search.sh
   ```

### Option 2: Manual Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

4. **Create directories**
   ```bash
   mkdir uploads chromadb_data logs
   ```

5. **Start the application**
   ```bash
   python run.py
   ```

## 🌐 Access the Application

Open your browser and go to: **http://localhost:5000**

## 📄 Test the System

1. **Upload a document**
   - Click the upload button in the sidebar
   - Select a PDF, DOCX, TXT, MD, or CSV file
   - Wait for processing to complete

2. **Ask questions**
   - Type: "What is this document about?"
   - Try: "Summarize the main points"
   - Ask: "Find information about [topic]"

3. **Try system commands**
   - "What can you do?"
   - "List my files"
   - "Show system stats"
   - "What time is it?"

## 🐳 Docker Quick Start

1. **Set up environment**
   ```bash
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   Open: http://localhost:5000

## 🔧 Configuration

### Required Environment Variables

**Required Environment Variables:**
- `GEMINI_API_KEY` - Your Google Gemini API key
- `SECRET_KEY` - Flask secret key (auto-generated by setup scripts)

**Setting GEMINI_API_KEY:**

**Option 1: Environment Variable (Recommended)**
```bash
# Windows
set GEMINI_API_KEY=your_gemini_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_gemini_api_key_here
```

**Option 2: .env file**
```bash
# Create .env file (SECRET_KEY auto-generated)
cp .env.example .env

# Edit .env file and uncomment/set:
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get your API key from:** https://makersuite.google.com/app/apikey

**Generate SECRET_KEY manually (if needed):**
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### Optional Configuration

```bash
FLASK_ENV=development
SECRET_KEY=your_secret_key
CHROMA_DB_PATH=./chromadb_data
UPLOAD_FOLDER=uploads
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=3
```

## 📚 Sample Documents

Upload the sample document provided in `sample_documents/sample_document.md` to test the system.

## 🆘 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **"GEMINI_API_KEY not set"**
   - Edit `.env` file
   - Add: `GEMINI_API_KEY=your_actual_api_key`

3. **Port 5000 already in use**
   - Change port in `run.py`
   - Or stop other services using port 5000

4. **File upload fails**
   - Check file size (max 16MB)
   - Verify file format (PDF, DOCX, TXT, MD, CSV)

### Getting Help

1. Check the full [README.md](README.md)
2. Review the [API documentation](README.md#api-reference)
3. Look at the logs in the terminal
4. Open an issue on GitHub

## 🎯 Next Steps

1. **Upload your documents** and start asking questions
2. **Explore different query types** (search, calculations, file operations)
3. **Try the API endpoints** for integration
4. **Customize the system** for your specific needs
5. **Deploy to production** using Docker

## 🔗 Useful Links

- [Full Documentation](README.md)
- [API Reference](README.md#api-reference)
- [Architecture Overview](README.md#architecture)
- [Deployment Guide](README.md#deployment-options)

---

**Need help?** The system includes built-in help - just ask "What can you do?" in the chat interface!
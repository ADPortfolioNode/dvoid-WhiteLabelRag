# Getting Started with WhiteLabelRAG

Welcome to WhiteLabelRAG! This guide will help you get up and running in just a few minutes.

## 🎯 What is WhiteLabelRAG?

WhiteLabelRAG is a complete Retrieval-Augmented Generation (RAG) application that allows you to:
- Upload documents and ask questions about them
- Have intelligent conversations with AI
- Process multiple document formats (PDF, DOCX, TXT, MD, CSV)
- Execute functions and perform calculations
- Get real-time responses with source citations

## 🚀 Quick Start (5 Minutes)

### Step 1: Get Your API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (keep it secure!)

### Step 2: Set Up the Environment

**Option A: Automated Setup (Recommended)**

Windows:
```cmd
scripts\setup.bat
```

Linux/Mac:
```bash
chmod +x scripts/*.sh
./scripts/setup.sh
```

**Option B: Manual Setup**

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Activate it
   # Windows:
   venv\Scripts\activate
   
   # Linux/Mac:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env file and add your API key
   # Or set as environment variable:
   export GEMINI_API_KEY=your_api_key_here
   ```

### Step 3: Verify Installation
```bash
python scripts/final-verification.py
```

### Step 4: Start the Application
```bash
python run.py
```

### Step 5: Open Your Browser
Go to: **http://localhost:5000**

## 🎮 First Steps

### 1. Test the System
Try these commands in the chat interface:
- "What can you do?"
- "What time is it?"
- "Calculate 15 * 23 + 7"

### 2. Upload a Document
1. Click the upload button in the sidebar
2. Select a PDF, Word document, or text file
3. Wait for processing to complete
4. Ask questions about your document!

### 3. Try Document Questions
- "What is this document about?"
- "Summarize the main points"
- "Find information about [specific topic]"

## 🛠️ Configuration Options

### Environment Variables

**Required:**
- `GEMINI_API_KEY` - Your Google Gemini API key

**Optional:**
```bash
FLASK_ENV=development          # Environment mode
SECRET_KEY=your_secret_key     # Flask secret key
CHUNK_SIZE=500                 # Document chunk size
CHUNK_OVERLAP=50               # Chunk overlap
TOP_K_RESULTS=3                # Number of search results
UPLOAD_FOLDER=uploads          # Upload directory
CHROMA_DB_PATH=./chromadb_data # Vector database path
```

### Performance Tuning

For better performance with large documents:
```bash
CHUNK_SIZE=300      # Smaller chunks for faster processing
CHUNK_OVERLAP=30    # Less overlap for speed
TOP_K_RESULTS=5     # More results for better accuracy
```

## 🐳 Docker Quick Start

If you prefer Docker:

1. **Set up environment:**
   ```bash
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

2. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   Open: http://localhost:5000

## 📚 What You Can Do

### Document Operations
- **Upload files**: "Upload this document"
- **List files**: "Show me my files"
- **File info**: "Tell me about document.pdf"
- **Process files**: "Process the uploaded document"

### Search and Questions
- **Document search**: "Find information about [topic]"
- **Summarization**: "Summarize this document"
- **Specific questions**: "What does the document say about [topic]?"
- **Comparisons**: "Compare the information about X and Y"

### System Functions
- **Time**: "What time is it?"
- **Calculations**: "Calculate 15 * 23 + 7"
- **Text operations**: "Convert 'hello world' to uppercase"
- **System info**: "Show system statistics"

### Conversational AI
- **General chat**: "How are you today?"
- **Help**: "What can you help me with?"
- **Explanations**: "Explain how RAG works"
- **Follow-up questions**: Continue conversations naturally

## 🔧 Troubleshooting

### Common Issues

**1. "GEMINI_API_KEY not set"**
```bash
# Set as environment variable
export GEMINI_API_KEY=your_api_key_here

# Or add to .env file
echo "GEMINI_API_KEY=your_api_key_here" >> .env
```

**2. "Module not found" errors**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

**3. "Port 5000 already in use"**
```bash
# Find what's using the port
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac

# Kill the process or change port in run.py
```

**4. File upload not working**
- Check file size (max 16MB)
- Verify file format (PDF, DOCX, TXT, MD, CSV)
- Ensure uploads directory exists

### Getting Help

1. **Run diagnostics:**
   ```bash
   python scripts/check-env.py      # Check environment
   python scripts/test-setup.py     # Test installation
   python scripts/health-check.py   # Health check (server running)
   ```

2. **Check logs:**
   - Look at console output when running `python run.py`
   - Check browser developer tools (F12) for JavaScript errors

3. **Documentation:**
   - [README.md](README.md) - Complete documentation
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed troubleshooting
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

## 🎯 Next Steps

### Explore Features
1. **Try different document types** - Upload PDFs, Word docs, text files
2. **Test RAG workflows** - Ask complex questions about your documents
3. **Use function execution** - Try calculations, time queries, text operations
4. **Explore the API** - Use the REST endpoints for integration

### Customize the System
1. **Adjust chunk sizes** for your document types
2. **Configure search parameters** for better results
3. **Modify the interface** to match your brand
4. **Add custom functions** to the FunctionAgent

### Deploy to Production
1. **Follow the deployment guide** in [DEPLOYMENT.md](DEPLOYMENT.md)
2. **Set up monitoring** and health checks
3. **Configure SSL** for secure access
4. **Set up backups** for your data

## 🌟 Advanced Usage

### API Integration
```python
import requests

# Send a message
response = requests.post('http://localhost:5000/api/decompose', 
                        json={'message': 'What is AI?'})
print(response.json())

# Upload a document
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/api/documents/upload_and_ingest_document', 
                           files=files)
print(response.json())
```

### WebSocket Integration
```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
    console.log('Connected to WhiteLabelRAG');
});

socket.emit('chat_message', {
    message: 'Hello, WhiteLabelRAG!',
    session_id: 'my-session'
});

socket.on('chat_response', (data) => {
    console.log('Response:', data.text);
    console.log('Sources:', data.sources);
});
```

### Custom Configuration
```python
# In your .env file
CHUNK_SIZE=300              # Smaller chunks for faster processing
CHUNK_OVERLAP=30            # Less overlap
TOP_K_RESULTS=5             # More search results
MAX_CONTENT_LENGTH=33554432 # 32MB file limit
```

## 🎉 You're Ready!

Congratulations! You now have WhiteLabelRAG running. Here's what you can do:

1. **Start uploading documents** and asking questions
2. **Explore the different features** and capabilities
3. **Integrate with your applications** using the API
4. **Customize the system** for your specific needs
5. **Deploy to production** when you're ready

Need help? Check out our comprehensive documentation or run the diagnostic scripts!

---

**Happy RAG-ing!** 🚀
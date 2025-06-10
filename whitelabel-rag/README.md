# WhiteLabelRAG - AI Assistant with Document Search

A scalable Retrieval-Augmented Generation (RAG) application that provides a conversational AI interface with document search capabilities, task decomposition, and guided execution.

## Features

- 🤖 **Conversational AI** - Natural language interaction with context awareness
- 📄 **Document Processing** - Upload and process PDF, DOCX, TXT, MD, and CSV files
- 🔍 **Advanced Search** - Multiple RAG workflows (Basic, Advanced, Recursive, Adaptive)
- 🌐 **Internet Search** - Fallback to internet search when documents don't contain the answer
- 🏗️ **Modular Architecture** - Hub-and-spoke model with specialized agents
- ⚡ **Real-time Updates** - WebSocket-based status updates and communication
- 🎯 **Task Decomposition** - Break down complex tasks into manageable steps
- 📊 **File Management** - Upload, process, and manage document collections

## What's New - June 2025 Update

### Internet Search Integration
We've added Google Custom Search integration to provide answers when your document repository doesn't contain the information:

- **Automatic Fallback**: When the RAG system can't find an answer, it automatically searches the internet
- **Explicit Search Option**: Force internet search with the `use_internet_search` parameter
- **Comprehensive Results**: Get both document-based and internet-based results in one response

### Enhanced Documentation
- **[GOOGLE_SEARCH_SETUP.md](GOOGLE_SEARCH_SETUP.md)**: Detailed guide for setting up Google Custom Search
- **[INTERNET_SEARCH_CHANGES.md](INTERNET_SEARCH_CHANGES.md)**: Summary of all internet search-related changes
- **Testing Scripts**: New scripts to verify your Google API configuration

## Setting Up Google Custom Search

For the internet search feature to work properly, you need to set up Google Custom Search API:

1. **Create a Google Custom Search Engine**
   - Go to [Programmable Search Engine](https://programmablesearchengine.google.com/about/)
   - Click "Get Started" to create a new search engine
   - Configure your search engine (you can choose to search the entire web)
   - Note your Search Engine ID (cx)

2. **Get a Google API Key**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create or select a project
   - Enable the "Custom Search API"
   - Create credentials and get your API key

3. **Configure WhiteLabelRAG**
   - Add your API key to .env file: `GOOGLE_API_KEY=your_api_key_here`
   - Add your Search Engine ID to .env file: `INTERNET_SEARCH_ENGINE_ID=your_search_engine_id_here`

For detailed instructions and troubleshooting, see [GOOGLE_SEARCH_SETUP.md](GOOGLE_SEARCH_SETUP.md).

When documents in the RAG system don't contain the answer to a user's question, the system will automatically fall back to internet search if these credentials are configured.

## Technology Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| Backend   | Python Flask (port 5000) | REST API server with CORS and modular design |
| Vector DB | ChromaDB (port 8000) | Stores document and step embeddings for semantic search |
| LLM Service | Gemini API (Google) | Powers the conversational AI and task processing |
| Frontend  | HTML/CSS/JavaScript + Bootstrap | Mobile-first, responsive UI with real-time updates |
| WebSockets | Flask-SocketIO | Real-time communication between client and server |

## Quick Start

### Prerequisites

- Python 3.9+
- Google Gemini API key
- Google API key for internet search (optional)
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whitelabel-rag
   ```

2. **Set up environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY and GOOGLE_API_KEY
   ```

4. **Run the application**

You can start the application using one of the following methods:

- **Using Docker Compose (Recommended)**

  From the `whitelabel-rag/scripts` directory, run:

  ```bat
  run-docker.bat
  ```

  This script will build and start the application, Redis, and optionally the Nginx reverse proxy.

- **Locally in Development Mode**

  From the `whitelabel-rag/scripts` directory, run one of the following scripts:

  - `run-local.bat`: Starts the application locally by setting necessary environment variables and running `python run.py`.
  - `run-dev.bat`: Starts the development environment with virtual environment activation, environment variable checks, and debug mode enabled.

Make sure to set the required environment variables such as `GEMINI_API_KEY` before running these scripts.

5. **Open your browser**
   Navigate to `http://localhost:5000`

### Docker Deployment

1. **Using Docker Compose (Recommended)**
   ```bash
   # Set your API key in .env file
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   
   # Start the application
   docker-compose up -d
   ```

2. **Using Docker directly**
   ```bash
   # Build the image
   docker build -t whitelabel-rag .
   
   # Run the container
   docker run -p 5000:5000 -e GEMINI_API_KEY=your_api_key whitelabel-rag
   ```

## Usage

### Document Upload and Processing

1. **Upload Documents**
   - Use the sidebar upload interface
   - Supported formats: PDF, DOCX, TXT, MD, CSV
   - Files are automatically processed and indexed

2. **Ask Questions**
   - Type questions about your documents
   - The AI will search and provide answers with source citations
   - Context is maintained across conversations

### Available Commands

- **Document Search**: "Find information about climate change"
- **File Operations**: "List my files", "Process document.pdf"
- **System Queries**: "What can you do?", "Show system stats"
- **Calculations**: "Calculate 15 * 23 + 7"
- **Date/Time**: "What time is it?", "What's tomorrow's date?"
- **Text Operations**: "Convert 'hello' to uppercase"

## Architecture

### Assistant Types

1. **Concierge Agent** - Main orchestrator and conversation manager
2. **SearchAgent** - Specialized for document retrieval and RAG operations
3. **FileAgent** - Handles file operations and document management
4. **FunctionAgent** - Executes specialized functions and API integrations

### RAG Workflows

1. **Basic RAG** - Simple query → retrieve → generate
2. **Advanced RAG** - Multi-stage with query processing and reranking
3. **Recursive RAG** - Multi-part queries with targeted retrieval
4. **Adaptive RAG** - Automatically selects optimal workflow

## API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/decompose` | POST | Process user messages and decompose tasks |
| `/api/execute` | POST | Execute decomposed task steps |
| `/api/files` | GET/POST | List or upload documents |
| `/api/query` | POST | Search documents using vector similarity |

### WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `chat_message` | Client → Server | Send chat messages |
| `chat_response` | Server → Client | Receive AI responses |
| `assistant_status` | Server → Client | Real-time status updates |

## Configuration

### Environment Variables

**Required:**
- `GEMINI_API_KEY` - Your Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- `SECRET_KEY` - Flask secret key for session security (auto-generated by setup scripts)

**Setting the API Key:**

Option 1 - Environment Variable (Recommended):
```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

Option 2 - .env File:
```bash
# Copy example file
cp .env.example .env

# Edit .env and add:
GEMINI_API_KEY=your_api_key_here
```

**Optional Configuration:**
```bash
FLASK_ENV=development
SECRET_KEY=your_secret_key
CHROMA_DB_PATH=./chromadb_data
UPLOAD_FOLDER=uploads
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=3
```

**Generate Secret Key:**
```bash
# Auto-generated by setup scripts, or manually:
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Or use the dedicated script:
python scripts/generate-secret-key.py
```

**Check Your Environment:**
```bash
python scripts/check-env.py
```

### File Limits

- Maximum file size: 16MB
- Supported formats: PDF, DOCX, TXT, MD, CSV
- Chunk size: 500 tokens (configurable)
- Chunk overlap: 50 tokens (configurable)

## Development

### Project Structure

```
whitelabel-rag/
├── app/
│   ├── api/                 # API routes
│   ├── main/                # Main routes and templates
│   ├── services/            # Business logic and agents
│   ├── static/              # Frontend assets
│   ├── templates/           # HTML templates
│   └── utils/               # Utility functions
├── uploads/                 # Document storage
├── chromadb_data/          # Vector database
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
└── docker-compose.yml      # Docker configuration
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

### Adding New Agents

1. Create a new agent class inheriting from `BaseAssistant`
2. Implement the `handle_message` method
3. Register the agent in the routing logic
4. Add configuration to `config.py`

## Troubleshooting

### Common Issues

1. **ChromaDB Connection Errors**
   - Check if ChromaDB path is writable
   - Verify no other processes are using the database
   - Clear `chromadb_data/` directory if corrupted

2. **File Upload Failures**
   - Check file size (max 16MB)
   - Verify file format is supported
   - Ensure upload directory has write permissions

3. **API Rate Limits**
   - Monitor Gemini API usage
   - Implement request throttling if needed
   - Consider caching frequent responses

### Performance Optimization

1. **Large Document Collections**
   - Increase system RAM
   - Optimize chunk size for your use case
   - Consider using external ChromaDB instance

2. **High Concurrent Users**
   - Use Redis for session storage
   - Deploy multiple Flask instances with load balancer
   - Optimize database queries

## Security Considerations

- Store API keys securely (environment variables)
- Implement authentication for production use
- Validate all file uploads
- Use HTTPS in production
- Regular security updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub

## Roadmap

- [ ] Multi-user support with authentication
- [ ] Advanced file format support (PowerPoint, Excel)
- [ ] Integration with external APIs
- [ ] Advanced analytics and reporting
- [ ] Mobile application
- [ ] Multi-language support
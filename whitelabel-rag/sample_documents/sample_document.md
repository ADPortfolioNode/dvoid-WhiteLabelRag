# Sample Document for WhiteLabelRAG Testing

## Introduction

This is a sample document to test the WhiteLabelRAG system. It contains various types of information that can be used to verify the document processing and retrieval capabilities.

## Technology Overview

WhiteLabelRAG is built using modern technologies:

- **Backend**: Python Flask with modular architecture
- **Vector Database**: ChromaDB for semantic search
- **AI Model**: Google Gemini for natural language processing
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **Real-time Communication**: WebSockets via Flask-SocketIO

## Key Features

### Document Processing
The system can process multiple document formats:
1. PDF files
2. Microsoft Word documents (DOCX)
3. Plain text files (TXT)
4. Markdown files (MD)
5. CSV spreadsheets

### RAG Workflows
Four different RAG workflows are implemented:

1. **Basic RAG**: Simple query → retrieve → generate workflow
2. **Advanced RAG**: Multi-stage processing with query expansion and reranking
3. **Recursive RAG**: Multi-part queries with targeted retrieval
4. **Adaptive RAG**: Automatically selects the optimal workflow

### Assistant Architecture
The system uses a hub-and-spoke model with specialized agents:

- **Concierge Agent**: Main orchestrator and conversation manager
- **SearchAgent**: Document retrieval and RAG operations
- **FileAgent**: File operations and document management
- **FunctionAgent**: Specialized function execution

## Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_api_key_here
FLASK_ENV=development
SECRET_KEY=your_secret_key
CHROMA_DB_PATH=./chromadb_data
UPLOAD_FOLDER=uploads
```

### Performance Settings
- Chunk Size: 500 tokens
- Chunk Overlap: 50 tokens
- Top-K Results: 3-5 documents
- Maximum File Size: 16MB

## Usage Examples

### Basic Queries
- "What is WhiteLabelRAG?"
- "How does the system work?"
- "What file formats are supported?"

### Document Search
- "Find information about RAG workflows"
- "Search for configuration details"
- "What are the key features?"

### System Operations
- "List my uploaded files"
- "Show system statistics"
- "What time is it?"

## Technical Details

### Vector Embeddings
The system uses Google's embedding model to create vector representations of document chunks. These embeddings enable semantic search capabilities that go beyond simple keyword matching.

### Conversation Context
The Concierge maintains conversation history for each user session, allowing for contextual responses and follow-up questions.

### Error Handling
Robust error handling ensures the system remains stable even when processing corrupted files or handling network issues.

## Security Considerations

- API keys are stored securely in environment variables
- File uploads are validated for type and size
- User input is sanitized to prevent injection attacks
- HTTPS should be used in production environments

## Deployment Options

### Local Development
```bash
python run.py
```

### Docker Deployment
```bash
docker-compose up -d
```

### Production Deployment
- Use a reverse proxy (Nginx)
- Enable HTTPS with SSL certificates
- Set up monitoring and logging
- Configure backup procedures

## Troubleshooting

### Common Issues
1. **ChromaDB Connection Errors**: Check file permissions and disk space
2. **File Upload Failures**: Verify file size and format
3. **API Rate Limits**: Monitor Gemini API usage
4. **Memory Issues**: Increase system RAM for large document collections

### Performance Optimization
- Optimize chunk size for your use case
- Use Redis for session storage in production
- Consider external ChromaDB instance for scaling
- Implement caching for frequent queries

## Future Enhancements

- Multi-user support with authentication
- Advanced file format support
- Integration with external APIs
- Mobile application
- Multi-language support
- Advanced analytics and reporting

## Conclusion

WhiteLabelRAG provides a comprehensive solution for building AI-powered document search and conversation systems. Its modular architecture and multiple RAG workflows make it suitable for various use cases, from simple document Q&A to complex task automation.

For more information, refer to the README.md file and API documentation.
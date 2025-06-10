"""
Pytest configuration and fixtures for WhiteLabelRAG tests
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch

# Set test environment variables before importing app modules
os.environ['FLASK_ENV'] = 'testing'
os.environ['TESTING'] = 'true'
os.environ['GEMINI_API_KEY'] = 'test-api-key-for-testing'
os.environ['CHROMA_DB_PATH'] = './chromadb_data'

@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    """Setup test environment before all tests."""
    # Create test directories
    test_dirs = ['./test_chromadb_data', './test_uploads']
    for test_dir in test_dirs:
        os.makedirs(test_dir, exist_ok=True)
    
    yield
    
    # Cleanup test directories after all tests
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir, ignore_errors=True)

@pytest.fixture
def app():
    """Create application for testing."""
    from app import create_app
    
    # Create app with test configuration
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'UPLOAD_FOLDER': './test_uploads',
        'CHROMA_DB_PATH': './test_chromadb_data'
    })
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def mock_chroma_service():
    """Mock ChromaDB service for testing."""
    mock_instance = MagicMock()
    mock_instance.store_document.return_value = 'test-doc-id'
    mock_instance.query_documents.return_value = {
        'documents': [['Test document content']],
        'metadatas': [[{'source': 'test.txt'}]],
        'distances': [[0.1]]
    }
    mock_instance.get_collection_stats.return_value = {
        'documents_count': 1,
        'steps_count': 0,
        'total_items': 1
    }
    
    # Patch all the places where ChromaService is used
    patches = [
        patch('app.services.chroma_service.ChromaService', return_value=mock_instance),
        patch('app.services.chroma_service.get_chroma_service_instance', return_value=mock_instance),
        patch('app.services.rag_manager.get_chroma_service_instance', return_value=mock_instance),
        # Removed patch for non-existent function in concierge.py
        # patch('app.services.concierge.get_chroma_service_instance', return_value=mock_instance),
    ]
    
    # Start all patches
    for p in patches:
        p.start()
    
    yield mock_instance
    
    # Stop all patches
    for p in patches:
        p.stop()

@pytest.fixture
def mock_llm_factory():
    """Mock LLM Factory for testing."""
    # Create a mock class that behaves like LLMFactory
    mock_llm_class = MagicMock()
    # Return a valid JSON string for task decomposition
    mock_llm_class.generate_response.side_effect = [
        '{"task_analysis": "Simple task", "estimated_duration": "5", "steps": [{"step_number": 1, "instruction": "Step 1 instruction", "suggested_agent_type": "SearchAgent", "dependencies": [], "complexity": "low", "estimated_time": "60"}]}',
        'Decomposed task',
        'Direct response',
        'simple_query'
    ]
    mock_llm_class.get_llm.return_value = MagicMock()
    mock_llm_class.classify_intent.return_value = 'simple_query'
    
    # Patch all the places where LLMFactory is imported
    patches = [
        patch('app.services.llm_factory.LLMFactory', mock_llm_class),
        patch('app.services.concierge.LLMFactory', mock_llm_class),
        patch('app.services.task_assistant.LLMFactory', mock_llm_class),
        patch('app.services.search_agent.LLMFactory', mock_llm_class),
        patch('app.services.rag_manager.LLMFactory', mock_llm_class),
    ]
    
    # Start all patches
    for p in patches:
        p.start()
    
    yield mock_llm_class
    
    # Stop all patches
    for p in patches:
        p.stop()

@pytest.fixture
def mock_rag_manager():
    """Mock RAG Manager for testing."""
    with patch('app.services.rag_manager.get_rag_manager') as mock:
        mock_instance = MagicMock()
        # Adjusted return values to match test expectations
        mock_instance.query_documents.side_effect = [
            {'text': 'Found document', 'sources': [], 'error': None},
            {'text': 'Decomposed task', 'sources': [], 'error': None},
            {'text': 'Direct response', 'sources': [], 'error': None}
        ]
        mock_instance.get_collection_stats.return_value = {
            'documents_count': 1
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_conversation_store():
    """Mock conversation store for testing."""
    with patch('app.services.conversation_store.get_conversation_store') as mock:
        mock_instance = MagicMock()
        mock_conversation = MagicMock()
        mock_conversation.add_message = MagicMock()
        mock_conversation.get_context_string.return_value = 'Test conversation context'
        mock_instance.get_conversation.return_value = mock_conversation
        mock_instance.get_conversation_stats.return_value = {
            'total_conversations': 1,
            'total_messages': 5,
            'avg_messages_per_conversation': 5.0
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture(autouse=True)
def mock_socketio():
    """Mock SocketIO for testing."""
    with patch('app.socketio') as mock:
        mock.emit = MagicMock()
        yield mock

@pytest.fixture
def sample_file_content():
    """Sample file content for testing."""
    return b"This is test file content for testing purposes."

@pytest.fixture
def temp_file(sample_file_content):
    """Create temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(sample_file_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)
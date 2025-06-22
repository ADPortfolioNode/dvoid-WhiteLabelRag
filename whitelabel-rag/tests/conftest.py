import os
import sys
import pytest

# Add the whitelabel-rag directory to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'whitelabel-rag')))

from app import create_app
from flask.testing import FlaskClient

@pytest.fixture(autouse=True)
def set_test_env_vars(monkeypatch):
    # Force FastAPI HTTP client mode for ChromaDB during tests to avoid embedded mode errors
    monkeypatch.setenv('CHROMA_SERVER_HOST', 'localhost')
    monkeypatch.setenv('USE_CHROMA_HTTP_CLIENT', 'true')
    monkeypatch.setenv('CHROMA_API_IMPL', 'chromadb.api.fastapi.FastAPI')
    monkeypatch.setenv('CHROMA_SERVER_HTTP_PORT', '8000')

@pytest.fixture
def app():
    app = create_app()
    # FastAPI app does not have 'config', so remove app.config.update
    # Instead, set testing flag via environment variable or app.state if needed
    yield app

import io
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_llm(monkeypatch):
    mock = MagicMock()
    mock.generate_text.return_value = '{"steps": [{"step_number": 1, "instruction": "Search for information about climate change", "suggested_agent_type": "SearchAgent"}]}'
    monkeypatch.setattr('app.services.llm_factory.LLMFactory.get_llm', lambda: mock)
    return mock

@pytest.fixture
def mock_chroma_service(monkeypatch):
    mock = MagicMock()
    mock.query_documents.return_value = {
        'documents': [['Document content']],
        'metadatas': [[{'source': 'test_source'}]],
        'distances': [[0.1]]
    }
    monkeypatch.setattr('app.services.chroma_service.get_chroma_service_instance', lambda: mock)
    monkeypatch.setattr('app.services.chroma_service.ChromaService', lambda: mock)
    # Patch document processor methods to avoid real PDF parsing errors
    monkeypatch.setattr('app.services.document_processor.DocumentProcessor._extract_text', lambda self, file_path: "Extracted text")
    monkeypatch.setattr('app.services.document_processor.DocumentProcessor._create_chunks', lambda self, text: ["chunk1", "chunk2"])
    monkeypatch.setattr('app.services.document_processor.DocumentProcessor.process_document', lambda self, file_path: {"success": True, "chunks": ["chunk1", "chunk2"]})
    # Patch ChromaService._setup_chroma to no-op to avoid real ChromaDB calls
    monkeypatch.setattr('app.services.chroma_service.ChromaService._setup_chroma', lambda self: None)
    return mock

@pytest.fixture
def temp_pdf(tmp_path):
    # Minimal valid PDF file content
    pdf_content = (
        b'%PDF-1.4\n'
        b'1 0 obj\n'
        b'<< /Type /Catalog /Pages 2 0 R >>\n'
        b'endobj\n'
        b'2 0 obj\n'
        b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n'
        b'endobj\n'
        b'3 0 obj\n'
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\n'
        b'endobj\n'
        b'4 0 obj\n'
        b'<< /Length 44 >>\n'
        b'stream\n'
        b'BT\n'
        b'/F1 24 Tf\n'
        b'100 700 Td\n'
        b'(Hello, PDF!) Tj\n'
        b'ET\n'
        b'endstream\n'
        b'endobj\n'
        b'xref\n'
        b'0 5\n'
        b'0000000000 65535 f \n'
        b'0000000010 00000 n \n'
        b'0000000060 00000 n \n'
        b'0000000117 00000 n \n'
        b'0000000211 00000 n \n'
        b'trailer\n'
        b'<< /Size 5 /Root 1 0 R >>\n'
        b'startxref\n'
        b'308\n'
        b'%%EOF\n'
    )
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(pdf_content)
    return pdf_file

@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()

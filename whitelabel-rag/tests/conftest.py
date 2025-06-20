import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from unittest.mock import MagicMock
import tempfile
import os

@pytest.fixture(scope="session")
def app():
    app = create_app()
    return app

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

@pytest.fixture(scope="function")
def mock_llm():
    mock = MagicMock()
    # You can add default return values or side effects if needed
    return mock

@pytest.fixture(scope="function")
def temp_pdf():
    # Create a temporary PDF file for testing
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    # Write a minimal valid PDF file
    temp_file.write(b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 24 Tf 100 700 Td (Hello PDF) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000212 00000 n \ntrailer\n<< /Root 1 0 R /Size 5 >>\nstartxref\n312\n%%EOF')
    temp_file.close()
    yield temp_file.name
    os.unlink(temp_file.name)

@pytest.fixture(scope="function")
def mock_chroma_service():
    mock = MagicMock()
    # You can add default return values or side effects if needed
    return mock

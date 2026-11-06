"""Smoke tests for services and utilities.

Pure-function checks plus import checks. No LLM calls, no Chroma calls,
no network.
"""

import os

import pytest


def test_allowed_file():
    from app.utils.file_utils import allowed_file

    assert allowed_file("notes.txt") is True
    assert allowed_file("report.pdf") is True
    assert allowed_file("data.docx") is True
    assert allowed_file("doc.md") is True
    assert allowed_file("table.csv") is True
    assert allowed_file("UPPER.PDF") is True
    assert allowed_file("app.exe") is False
    assert allowed_file("noextension") is False


def test_get_file_extension_and_human_size():
    from app.utils.file_utils import get_file_extension, get_file_size_human

    assert get_file_extension("archive.tar.gz") == "gz"
    assert get_file_extension("plain") == ""
    assert get_file_size_human(0) == "0 B"
    assert get_file_size_human(2048) == "2.0 KB"


def test_config_requires_api_key(monkeypatch):
    # Config reads the key into a class attribute at import time, so the
    # missing-key path is exercised by clearing the attribute, not the env.
    from app.config import Config

    monkeypatch.setattr(Config, "GEMINI_API_KEY", "")
    with pytest.raises(ValueError):
        Config.validate_config()


def test_config_accepts_api_key(monkeypatch):
    from app.config import Config

    monkeypatch.setattr(Config, "GEMINI_API_KEY", "test-key")
    assert Config.validate_config() is True


def test_service_modules_import():
    import app.services.concierge  # noqa: F401
    import app.services.rag_manager  # noqa: F401
    import app.services.chroma_service  # noqa: F401
    import app.services.document_processor  # noqa: F401
    import app.services.file_manager  # noqa: F401

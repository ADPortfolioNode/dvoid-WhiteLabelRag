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


def test_chroma_init_failure_does_not_poison_retry(monkeypatch, tmp_path):
    """A failed first Chroma init must not wedge the service: the next
    call retries setup instead of returning a half-built instance."""
    import app.services.chroma_service as cs

    monkeypatch.setenv("CHROMA_DB_PATH", str(tmp_path / "chroma"))
    monkeypatch.setattr(cs, "_chroma_service_instance", None)
    # Skip real embedding setup (would download models); the test is about
    # the singleton/retry behaviour, not embeddings.
    monkeypatch.setattr(
        cs.ChromaService,
        "_setup_embedding_function",
        lambda self: setattr(self, "embedding_function", object()),
    )

    calls = {"n": 0}

    class FakeClient:
        def get_or_create_collection(self, **kwargs):
            return object()

    def flaky_client(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("simulated first-init failure")
        return FakeClient()

    monkeypatch.setattr(cs.chromadb, "PersistentClient", flaky_client)

    with pytest.raises(RuntimeError, match="simulated first-init failure"):
        cs.get_chroma_service_instance()
    # Nothing cached after the failure, so the next call retries.
    assert cs._chroma_service_instance is None
    svc = cs.get_chroma_service_instance()
    assert svc is not None
    assert svc.client is not None
    # And a healthy instance is still cached afterwards.
    assert cs.get_chroma_service_instance() is svc

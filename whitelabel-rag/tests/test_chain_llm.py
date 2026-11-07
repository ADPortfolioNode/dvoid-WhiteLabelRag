"""Tests for the multi-provider LLM fallback chain (PocketPro chain).

No network, no real LLM calls: the HTTP rungs are faked by patching
urllib.request.urlopen, and the Gemini rung is stubbed. The chain
order and the retrieved-text fallback are what these tests pin.
"""

import io
import json

import pytest

from app.services.chain_llm import ChainLLM
from app.services.llm_factory import LLMFactory


class FakeResponse:
    """Minimal urlopen response: context manager with .read()."""

    def __init__(self, payload):
        self._data = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self._data


def _raise(*args, **kwargs):
    raise RuntimeError("429")


@pytest.fixture(autouse=True)
def reset_chain_state():
    ChainLLM.last_provider = None
    ChainLLM.last_error = None
    yield
    ChainLLM.last_provider = None
    ChainLLM.last_error = None


@pytest.fixture(autouse=True)
def clear_chain_keys(monkeypatch):
    for key in ("GROQ_API_KEY", "OLLAMA_ENABLED", "OLLAMA_HOST",
                "OLLAMA_MODEL", "GROQ_MODEL"):
        monkeypatch.delenv(key, raising=False)
    yield


def _openai_payload(text):
    return {"choices": [{"message": {"role": "assistant", "content": text}}]}


def _ollama_payload(text):
    return {"message": {"role": "assistant", "content": text}}


def test_chain_falls_back_to_groq_when_gemini_fails(monkeypatch):
    monkeypatch.setattr(ChainLLM, "_call_gemini", classmethod(_raise))
    monkeypatch.setenv("GROQ_API_KEY", "fake-groq-key")
    calls = []

    def fake_urlopen(request, timeout=None):
        calls.append(request)
        return FakeResponse(_openai_payload("groq answer"))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    text, provider = ChainLLM.generate("hello")
    assert text == "groq answer"
    assert provider == "groq"
    assert len(calls) == 1
    assert "api.groq.com" in calls[0].full_url


def test_chain_skips_unconfigured_rungs(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    calls = []
    monkeypatch.setattr("urllib.request.urlopen",
                        lambda *a, **k: calls.append(a) or FakeResponse({}))
    text, provider = ChainLLM.generate("hello")
    assert text is None
    assert provider is None
    assert calls == []


def test_chain_ollama_only_when_enabled(monkeypatch):
    monkeypatch.setattr(ChainLLM, "_call_gemini", classmethod(_raise))
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    calls = []
    monkeypatch.setattr("urllib.request.urlopen",
                        lambda request, timeout=None: calls.append(request) or FakeResponse(_ollama_payload("ollama answer")))
    # Not enabled: Ollama is skipped, chain is empty.
    text, provider = ChainLLM.generate("hello")
    assert text is None and provider is None
    assert calls == []
    # Enabled: Ollama answers.
    monkeypatch.setenv("OLLAMA_ENABLED", "1")
    text, provider = ChainLLM.generate("hello")
    assert text == "ollama answer"
    assert provider == "ollama"
    assert calls[0].full_url.endswith("/api/chat")


def test_chain_groq_request_shape(monkeypatch):
    monkeypatch.setattr(ChainLLM, "_call_gemini", classmethod(_raise))
    monkeypatch.setenv("GROQ_API_KEY", "fake-groq-key")
    captured = {}

    def fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["auth"] = request.get_header("Authorization")
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse(_openai_payload("ok"))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    ChainLLM.generate("hi", system_prompt="Be helpful", temperature=0.1)
    assert captured["url"] == "https://api.groq.com/openai/v1/chat/completions"
    assert captured["auth"] == "Bearer fake-groq-key"
    assert captured["body"]["model"] == "openai/gpt-oss-20b"
    assert captured["body"]["messages"][0] == {"role": "system", "content": "Be helpful"}
    assert captured["body"]["messages"][1] == {"role": "user", "content": "hi"}
    assert captured["body"]["temperature"] == 0.1


def test_chain_records_last_provider(monkeypatch):
    monkeypatch.setattr(ChainLLM, "_call_gemini", classmethod(_raise))
    monkeypatch.setenv("GROQ_API_KEY", "fake-groq-key")
    monkeypatch.setattr("urllib.request.urlopen",
                        lambda *a, **k: FakeResponse(_openai_payload("ok")))
    ChainLLM.generate("hi")
    assert ChainLLM.last_provider == "groq"
    status = ChainLLM.status()
    assert status["provider"] == "groq"
    assert status["chain"] == ["gemini", "groq", "ollama"]
    assert [p["name"] for p in status["providers"]] == status["chain"]


def test_generate_response_falls_back_to_retrieved_text(monkeypatch):
    monkeypatch.setattr(ChainLLM, "generate",
                        classmethod(lambda cls, *a, **k: (None, None)))
    prompt = "Context:\nThe zebra migration starts in March.\n\nQuestion: When does it start?"
    text = LLMFactory.generate_response(prompt)
    assert "The zebra migration starts in March." in text
    assert "Error generating response" not in text
    assert "No LLM provider" in text


def test_generate_response_falls_back_without_context(monkeypatch):
    monkeypatch.setattr(ChainLLM, "generate",
                        classmethod(lambda cls, *a, **k: (None, None)))
    text = LLMFactory.generate_response("plain question, no context")
    assert "No LLM provider was available" in text
    assert "Error generating response" not in text


def test_gemini_rung_is_bounded_by_timeout(monkeypatch):
    """A hung Gemini call must not wedge the chain: the rung passes a
    timeout to generate_content (the 180s live-query hang caught this)."""
    captured = {}

    class FakeModel:
        def generate_content(self, contents, generation_config=None,
                             request_options=None):
            captured["request_options"] = request_options
            raise RuntimeError("boom")

    monkeypatch.setattr(LLMFactory, "get_llm",
                        classmethod(lambda cls, task="general": FakeModel()))
    with pytest.raises(RuntimeError, match="boom"):
        ChainLLM._call_gemini("hi", None, 0.2, 1024, "general")
    from app.services.chain_llm import REQUEST_TIMEOUT
    assert captured["request_options"] == {"timeout": REQUEST_TIMEOUT}


def test_gemini_rung_wall_clock_timeout(monkeypatch):
    """request_options alone does not bound a Gemini call that stalls
    before the RPC starts (TLS/proxy handshake): the live query hung
    240s with no timeout fired. The worker-thread timeout must fire."""
    import time

    import app.services.chain_llm as chain_module

    class HangingModel:
        def generate_content(self, contents, generation_config=None,
                             request_options=None):
            time.sleep(10)

    monkeypatch.setattr(LLMFactory, "get_llm",
                        classmethod(lambda cls, task="general": HangingModel()))
    monkeypatch.setattr(chain_module, "REQUEST_TIMEOUT", 1)
    start = time.monotonic()
    with pytest.raises(RuntimeError, match="timed out"):
        ChainLLM._call_gemini("hi", None, 0.2, 1024, "general")
    assert time.monotonic() - start < 5


def test_llm_status_endpoint(app):
    client = app.test_client()
    resp = client.get("/api/llm/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["chain"] == ["gemini", "groq", "ollama"]
    assert [p["name"] for p in data["providers"]] == data["chain"]
    gemini = data["providers"][0]
    assert gemini["name"] == "gemini"
    assert gemini["available"] is True  # conftest sets a test GEMINI_API_KEY
    assert data["providers"][1]["available"] is False  # no GROQ_API_KEY

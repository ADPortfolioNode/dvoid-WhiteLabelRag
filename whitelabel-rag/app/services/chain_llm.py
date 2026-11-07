"""
Multi-provider LLM fallback chain for WhiteLabelRAG.

Ports the PocketPro / funkStudio ChainLLM (standard chain): Gemini
first, then Groq, then local Ollama (only when OLLAMA_ENABLED is
set), then retrieved text. Every rung after Gemini is stdlib-only
(urllib) — no new dependencies. A rung with no key configured is
skipped.

The chain is used by LLMFactory.generate_response, so every caller
(rag_manager, concierge, task_assistant, search_agent) gets the
fallback for free. ChainLLM.last_provider records which rung
answered the most recent call; /api/llm/status exposes it.
"""

import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

# Provider defaults — the same values the PocketPro chain uses.
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL_DEFAULT = "openai/gpt-oss-20b"
OLLAMA_HOST_DEFAULT = "http://localhost:11434"
OLLAMA_MODEL_DEFAULT = "llama3.1"

# One rung gets this long before the chain moves on. Deliberately
# bounded: a hung provider must not wedge the request.
REQUEST_TIMEOUT = 30

# Chain order, matching the PocketPro standard chain.
CHAIN_ORDER = ["gemini", "groq", "ollama"]


def _env_flag(name):
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


class ChainLLM:
    """Ordered LLM fallback chain. All methods are classmethods."""

    last_provider = None
    last_error = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @classmethod
    def generate(cls, prompt, system_prompt=None, temperature=0.2,
                 max_tokens=1024, task="general"):
        """Try each rung in order.

        Returns (text, provider) on the first success, or (None, None)
        when every rung failed or was unconfigured. The caller falls
        back to retrieved text in that case.
        """
        for name in CHAIN_ORDER:
            if not cls._is_configured(name):
                continue
            try:
                text = cls._call_rung(name, prompt, system_prompt,
                                      temperature, max_tokens, task)
            except Exception as exc:  # noqa: BLE001 - one rung must not kill the chain
                logger.warning("LLM rung %s failed: %s", name, exc)
                cls.last_error = "%s: %s" % (name, exc)
                continue
            if text:
                cls.last_provider = name
                cls.last_error = None
                logger.info("LLM answered via %s", name)
                return text, name
            logger.warning("LLM rung %s returned no text", name)
        cls.last_provider = None
        return None, None

    @classmethod
    def providers(cls):
        """Ordered provider descriptors for /api/llm/status."""
        return [
            {
                "name": "gemini",
                "available": bool(os.environ.get("GEMINI_API_KEY", "").strip()),
                "model": os.environ.get("GEMINI_MODEL", "") or "gemini-1.5-flash",
            },
            {
                "name": "groq",
                "available": bool(os.environ.get("GROQ_API_KEY", "").strip()),
                "model": os.environ.get("GROQ_MODEL", GROQ_MODEL_DEFAULT),
            },
            {
                "name": "ollama",
                "available": _env_flag("OLLAMA_ENABLED"),
                "model": os.environ.get("OLLAMA_MODEL", OLLAMA_MODEL_DEFAULT),
            },
        ]

    @classmethod
    def status(cls):
        """Chain status for /api/llm/status."""
        return {
            "provider": cls.last_provider,
            "providers": cls.providers(),
            "chain": list(CHAIN_ORDER),
            "last_error": cls.last_error,
        }

    # ------------------------------------------------------------------
    # Rung dispatch
    # ------------------------------------------------------------------
    @classmethod
    def _is_configured(cls, name):
        if name == "gemini":
            return bool(os.environ.get("GEMINI_API_KEY", "").strip())
        if name == "groq":
            return bool(os.environ.get("GROQ_API_KEY", "").strip())
        if name == "ollama":
            return _env_flag("OLLAMA_ENABLED")
        return False

    @classmethod
    def _call_rung(cls, name, prompt, system_prompt, temperature,
                   max_tokens, task):
        if name == "gemini":
            return cls._call_gemini(prompt, system_prompt, temperature,
                                    max_tokens, task)
        if name == "groq":
            return cls._call_openai_compatible(
                GROQ_BASE_URL, os.environ["GROQ_API_KEY"],
                os.environ.get("GROQ_MODEL", GROQ_MODEL_DEFAULT),
                prompt, system_prompt, temperature, max_tokens)
        if name == "ollama":
            return cls._call_ollama(prompt, system_prompt, temperature,
                                    max_tokens)
        raise ValueError("unknown LLM rung: %s" % name)

    # ------------------------------------------------------------------
    # Rungs
    # ------------------------------------------------------------------
    @classmethod
    def _call_gemini(cls, prompt, system_prompt, temperature, max_tokens,
                     task):
        """Gemini rung, reusing LLMFactory's model selection."""
        # Deferred import: llm_factory imports this module.
        from app.services.llm_factory import LLMFactory

        import google.generativeai as genai

        llm = LLMFactory.get_llm(task)
        full_prompt = prompt
        if system_prompt:
            full_prompt = "System: %s\n\nUser: %s" % (system_prompt, prompt)
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        # Bound the call twice. request_options bounds the RPC itself,
        # but a hung Gemini request can stall before the RPC starts
        # (TLS/proxy handshake retries), which that timeout does not
        # cover — the live query proved it: 240s with no timeout fired.
        # So the call also runs in a worker thread with a wall-clock
        # timeout; on expiry the rung fails and the chain moves on.
        # The stray thread is left running (daemon) and does not block.
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

        def _do_call():
            return llm.generate_content(
                full_prompt, generation_config=generation_config,
                request_options={"timeout": REQUEST_TIMEOUT})

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(_do_call)
        try:
            response = future.result(timeout=REQUEST_TIMEOUT)
        except FuturesTimeoutError:
            raise RuntimeError(
                "Gemini call timed out after %ss" % REQUEST_TIMEOUT) from None
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
        return response.text

    @classmethod
    def _call_openai_compatible(cls, base_url, api_key, model, prompt,
                                system_prompt, temperature, max_tokens):
        """Groq rung (OpenAI-compatible chat completions)."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }).encode("utf-8")
        request = urllib.request.Request(
            base_url.rstrip("/") + "/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer %s" % api_key,
                "User-Agent": "WhiteLabelRAG/1.0",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            raise RuntimeError("HTTP %s: %s" % (exc.code, detail)) from exc
        choices = body.get("choices") or []
        if not choices:
            raise RuntimeError("no choices in response: %s" % str(body)[:300])
        content = ((choices[0].get("message") or {}).get("content") or "").strip()
        if not content:
            raise RuntimeError("empty content in response")
        return content

    @classmethod
    def _call_ollama(cls, prompt, system_prompt, temperature, max_tokens):
        """Local Ollama rung. Only reached when OLLAMA_ENABLED is set."""
        host = os.environ.get("OLLAMA_HOST", OLLAMA_HOST_DEFAULT).rstrip("/")
        model = os.environ.get("OLLAMA_MODEL", OLLAMA_MODEL_DEFAULT)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }).encode("utf-8")
        request = urllib.request.Request(
            host + "/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            raise RuntimeError("HTTP %s: %s" % (exc.code, detail)) from exc
        content = ((body.get("message") or {}).get("content") or "").strip()
        if not content:
            raise RuntimeError("empty content in response")
        return content

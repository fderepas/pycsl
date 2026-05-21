"""
Embedding adapter — mirrors llm_client.py's backend-agnostic pattern.

Supports Ollama's /api/embed endpoint for local embedding models.
Environment variables (override config):
    OLLAMA_URL       Ollama base URL  (config key: nomic-embed-text-ollama-url)
    EMBEDDING_MODEL  Embedding model  (default: nomic-embed-text)
"""

import json
import os
import sys
import urllib.request
import urllib.error
from typing import List


def _load_ollama_url() -> str:
    """Read Ollama URL from env var, falling back to agents-config.json."""
    env = os.environ.get("OLLAMA_URL")
    if env:
        return env
    config_path = os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir, "config", "agents-config.json"
    )
    try:
        with open(os.path.normpath(config_path)) as f:
            cfg = json.load(f)
        return cfg.get("nomic-embed-text-ollama-url", "http://127.0.0.1:11434")
    except (FileNotFoundError, json.JSONDecodeError):
        return "http://127.0.0.1:11434"


OLLAMA_URL = _load_ollama_url()
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")

# nomic-embed-text context window is 8192 tokens.
# Conservative limit: ~3 chars/token for code-heavy content.
_MAX_CHARS = 6000


def _ollama_post(texts: List[str], model: str) -> List[List[float]]:
    """Send a single /api/embed request. Raises on HTTP error."""
    body = {"model": model, "input": texts}
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embed",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["embeddings"]


def ollama_embed(texts: List[str], model: str | None = None) -> List[List[float]]:
    """Embed a list of texts using Ollama's /api/embed endpoint.

    Truncates oversized inputs and falls back to one-by-one embedding
    if a batch request fails with HTTP 400.
    """
    model = model or EMBEDDING_MODEL
    safe_texts = [t[:_MAX_CHARS] if len(t) > _MAX_CHARS else t for t in texts]

    try:
        return _ollama_post(safe_texts, model)
    except urllib.error.HTTPError as e:
        if e.code != 400:
            raise
        # Batch failed — fall back to embedding one at a time
        print(f"    Batch of {len(safe_texts)} failed (400), retrying individually…",
              file=sys.stderr)
        results: List[List[float]] = []
        for i, text in enumerate(safe_texts):
            limit = _MAX_CHARS
            while limit >= 500:
                try:
                    emb = _ollama_post([text[:limit]], model)
                    results.extend(emb)
                    break
                except urllib.error.HTTPError as e2:
                    if e2.code != 400:
                        raise
                    # Halve and retry
                    limit //= 2
                    print(f"      chunk {i}: truncating to {limit} chars",
                          file=sys.stderr)
            else:
                raise RuntimeError(
                    f"Chunk {i} still fails at {limit} chars — content may be unparseable"
                )
        return results


def embed(text: str, model: str | None = None) -> List[float]:
    """Embed a single text string. Convenience wrapper around embed_batch."""
    return embed_batch([text], model)[0]


def embed_batch(texts: List[str], model: str | None = None) -> List[List[float]]:
    """Embed a batch of texts using the configured backend.

    Currently only Ollama is supported. Extend here for OpenAI, etc.
    """
    return ollama_embed(texts, model)

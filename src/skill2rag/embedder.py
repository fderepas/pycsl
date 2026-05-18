"""
Embedding adapter — mirrors llm_client.py's backend-agnostic pattern.

Supports Ollama's /api/embed endpoint for local embedding models.
Environment variables (override config):
    OLLAMA_URL       Ollama base URL  (config key: nomic-embed-text-ollama-url)
    EMBEDDING_MODEL  Embedding model  (default: nomic-embed-text)
"""

import json
import os
import urllib.request
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


def ollama_embed(texts: List[str], model: str | None = None) -> List[List[float]]:
    """Embed a list of texts using Ollama's /api/embed endpoint.

    Args:
        texts:  List of strings to embed.
        model:  Ollama model name (default: EMBEDDING_MODEL env var).

    Returns:
        List of embedding vectors (one per input text).
    """
    model = model or EMBEDDING_MODEL
    body = {
        "model": model,
        "input": texts,
    }
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embed",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["embeddings"]


def embed(text: str, model: str | None = None) -> List[float]:
    """Embed a single text string. Convenience wrapper around embed_batch."""
    return embed_batch([text], model)[0]


def embed_batch(texts: List[str], model: str | None = None) -> List[List[float]]:
    """Embed a batch of texts using the configured backend.

    Currently only Ollama is supported. Extend here for OpenAI, etc.
    """
    return ollama_embed(texts, model)

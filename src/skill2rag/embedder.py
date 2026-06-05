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
import time
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

# Per-request timeout + retry budget (env-tunable). The old single 300 s timeout
# with no retry meant a transient Ollama stall (cold model load / busy host)
# blocked one batch for up to 5 minutes with no recovery — over many batches the
# build looked like an indefinite hang. A shorter timeout + bounded retry with
# backoff fails fast and recovers from a momentary stall instead.
_TIMEOUT = int(os.environ.get("EMBED_TIMEOUT", "60"))     # seconds per request
_MAX_RETRIES = int(os.environ.get("EMBED_RETRIES", "3"))  # attempts on conn/timeout
_BACKOFF_BASE = 2                                          # seconds (doubles each retry)


def _ollama_post(texts: List[str], model: str) -> List[List[float]]:
    """Send a single /api/embed request, retrying on connection/timeout errors.

    HTTP status errors (e.g. 400) propagate immediately — the caller handles
    those with its one-by-one fallback. Only transient transport failures
    (connection refused, socket timeout, DNS) are retried, with exponential
    backoff; after `_MAX_RETRIES` a clear RuntimeError names the URL/model."""
    body = {"model": model, "input": texts}
    data = json.dumps(body).encode("utf-8")
    last_reason = None
    for attempt in range(1, _MAX_RETRIES + 1):
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/embed",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))["embeddings"]
        except urllib.error.HTTPError:
            raise  # HTTP status (e.g. 400) — handled by the caller's fallback
        except OSError as e:
            # Catch OSError, not just urllib.error.URLError: a connection-phase
            # failure is wrapped in URLError, but a *read*-phase socket timeout
            # raises a bare TimeoutError (== socket.timeout, an OSError subclass)
            # that URLError does NOT wrap — so the narrower except missed it and
            # the retry never engaged. OSError covers URLError, TimeoutError,
            # ConnectionError, and DNS failures; HTTPError (re-raised above) is
            # excluded. `reason` exists only on URLError — fall back to the error.
            reason = getattr(e, "reason", None) or e
            last_reason = reason
            if attempt < _MAX_RETRIES:
                backoff = _BACKOFF_BASE * (2 ** (attempt - 1))
                print(f"    Ollama embed attempt {attempt}/{_MAX_RETRIES} failed "
                      f"({reason}); retrying in {backoff}s…",
                      file=sys.stderr, flush=True)
                time.sleep(backoff)
    raise RuntimeError(
        f"Ollama embedding at {OLLAMA_URL}/api/embed failed after {_MAX_RETRIES} "
        f"attempts ({last_reason}). Is Ollama running and the '{EMBEDDING_MODEL}' "
        f"model pulled? Tune with EMBED_TIMEOUT / EMBED_RETRIES, or point elsewhere "
        f"with OLLAMA_URL.")


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

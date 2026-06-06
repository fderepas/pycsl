"""Integration tests for skill2rag.

These tests require a running Ollama instance with the nomic-embed-text model.
All tests are skipped automatically if Ollama is not reachable.

Run with:  make test-integration
"""

import json
import os
import urllib.request
from pathlib import Path

import numpy as np
import pytest

# Use localhost unless overridden
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
EMBEDDING_MODEL = "nomic-embed-text"


def _ollama_available() -> bool:
    """Check if Ollama is reachable and nomic-embed-text is installed."""
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        model_names = [m["name"] for m in data.get("models", [])]
        return any(EMBEDDING_MODEL in name for name in model_names)
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _ollama_available(),
    reason=f"Ollama not reachable at {OLLAMA_URL} or {EMBEDDING_MODEL} not installed",
)


# ---- Ollama health check ----

class TestOllamaAvailability:
    def test_server_reachable(self):
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        assert "models" in data

    def test_embedding_model_present(self):
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        model_names = [m["name"] for m in data.get("models", [])]
        assert any(EMBEDDING_MODEL in name for name in model_names), \
            f"{EMBEDDING_MODEL} not found in: {model_names}"


# ---- Embedding ----

class TestEmbedding:
    def test_embed_single(self):
        os.environ["OLLAMA_URL"] = OLLAMA_URL
        from skill2rag.embedder import embed
        vec = embed("Hello, world!", EMBEDDING_MODEL)
        assert isinstance(vec, list)
        assert len(vec) > 0
        assert all(isinstance(v, float) for v in vec)

    def test_embed_batch(self):
        os.environ["OLLAMA_URL"] = OLLAMA_URL
        from skill2rag.embedder import embed_batch
        texts = ["First text", "Second text", "Third text"]
        vecs = embed_batch(texts, EMBEDDING_MODEL)
        assert len(vecs) == 3
        # All vectors should have the same dimensionality
        dims = {len(v) for v in vecs}
        assert len(dims) == 1
        assert dims.pop() > 0

    def test_embed_dimension_consistency(self):
        os.environ["OLLAMA_URL"] = OLLAMA_URL
        from skill2rag.embedder import embed
        v1 = embed("short", EMBEDDING_MODEL)
        v2 = embed("a much longer piece of text with more words", EMBEDDING_MODEL)
        assert len(v1) == len(v2)

    def test_similar_texts_closer_than_unrelated(self):
        os.environ["OLLAMA_URL"] = OLLAMA_URL
        from skill2rag.embedder import embed_batch
        from skill2rag.retriever import _cosine_similarity
        vecs = embed_batch([
            "How to annotate a Python loop with an invariant",
            "Writing loop invariant annotations in Python",
            "The weather forecast for tomorrow is sunny",
        ], EMBEDDING_MODEL)
        arr = np.array(vecs, dtype=np.float32)
        query = arr[0]
        scores = _cosine_similarity(query, arr[1:])
        # "loop invariant" text should be more similar than "weather"
        assert scores[0] > scores[1], \
            f"Similar text ({scores[0]:.4f}) should score higher than unrelated ({scores[1]:.4f})"


# ---- Build index + query ----

class TestBuildAndQuery:
    @pytest.fixture
    def index_path(self, tmp_path):
        return str(tmp_path / "test_index.json")

    def test_build_index_from_examples(self, index_path):
        os.environ["OLLAMA_URL"] = OLLAMA_URL
        from skill2rag.indexer import build_index
        examples_dir = str(Path(__file__).resolve().parents[2] / "examples")
        build_index(
            skill_dir=examples_dir,
            index_path=index_path,
            model=EMBEDDING_MODEL,
        )
        # Index file should exist and be valid JSON
        data = json.loads(Path(index_path).read_text(encoding="utf-8"))
        assert data["model"] == EMBEDDING_MODEL
        assert len(data["chunks"]) > 0
        assert len(data["embeddings"]) == len(data["chunks"])
        # Each embedding should be a list of floats
        assert len(data["embeddings"][0]) > 0

    def test_query_returns_relevant_chunks(self, index_path):
        os.environ["OLLAMA_URL"] = OLLAMA_URL
        from skill2rag.indexer import build_index
        from skill2rag.retriever import retrieve_with_scores
        examples_dir = str(Path(__file__).resolve().parents[2] / "examples")
        build_index(
            skill_dir=examples_dir,
            index_path=index_path,
            model=EMBEDDING_MODEL,
        )
        results = retrieve_with_scores(
            query="How to annotate a loop with an invariant in PyCSL?",
            index_path=index_path,
            top_k=5,
        )
        assert len(results) == 5
        # All scores should be floats
        for chunk, score in results:
            assert isinstance(score, float)
        # Top result should come from the annotate skill
        top_sources = [chunk.source_file for chunk, _ in results[:3]]
        assert "annotate" in top_sources, \
            f"Expected 'annotate' in top-3 sources, got: {top_sources}"

    def test_query_top_k_respected(self, index_path):
        os.environ["OLLAMA_URL"] = OLLAMA_URL
        from skill2rag.indexer import build_index
        from skill2rag.retriever import retrieve
        examples_dir = str(Path(__file__).resolve().parents[2] / "examples")
        build_index(
            skill_dir=examples_dir,
            index_path=index_path,
            model=EMBEDDING_MODEL,
        )
        for k in [1, 3, 10]:
            results = retrieve(
                query="WhyML transpiler",
                index_path=index_path,
                top_k=k,
            )
            assert len(results) == k

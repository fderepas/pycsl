"""Unit tests for skill2rag.retriever (cosine similarity and index loading)."""

import json
from pathlib import Path

import numpy as np
import pytest

from skill2rag.chunker import Chunk
from skill2rag.retriever import _cosine_similarity, _load_index


class TestCosineSimilarity:
    def test_identical_vectors(self):
        q = np.array([1.0, 0.0, 0.0])
        m = np.array([[1.0, 0.0, 0.0]])
        scores = _cosine_similarity(q, m)
        assert scores[0] == pytest.approx(1.0, abs=1e-6)

    def test_orthogonal_vectors(self):
        q = np.array([1.0, 0.0, 0.0])
        m = np.array([[0.0, 1.0, 0.0]])
        scores = _cosine_similarity(q, m)
        assert scores[0] == pytest.approx(0.0, abs=1e-6)

    def test_opposite_vectors(self):
        q = np.array([1.0, 0.0])
        m = np.array([[-1.0, 0.0]])
        scores = _cosine_similarity(q, m)
        assert scores[0] == pytest.approx(-1.0, abs=1e-6)

    def test_ranking_order(self):
        q = np.array([1.0, 0.0, 0.0])
        m = np.array([
            [0.0, 1.0, 0.0],   # orthogonal → 0
            [1.0, 0.0, 0.0],   # identical → 1
            [0.5, 0.5, 0.0],   # partial → ~0.7
        ])
        scores = _cosine_similarity(q, m)
        ranked = np.argsort(scores)[::-1]
        assert ranked[0] == 1  # identical first
        assert ranked[-1] == 0  # orthogonal last

    def test_multiple_rows(self):
        q = np.array([1.0, 1.0])
        m = np.array([
            [1.0, 1.0],
            [1.0, 0.0],
            [0.0, 1.0],
        ])
        scores = _cosine_similarity(q, m)
        assert len(scores) == 3
        assert scores[0] == pytest.approx(1.0, abs=1e-6)


class TestLoadIndex:
    def test_deserializes_correctly(self, tmp_path):
        index_data = {
            "model": "test-model",
            "chunks": [
                {
                    "chunk_id": "src::Title",
                    "source_file": "src",
                    "heading_path": ["Title"],
                    "title": "Title",
                    "content": "Some content",
                    "content_hash": "abc123",
                    "level": 1,
                }
            ],
            "embeddings": [[0.1, 0.2, 0.3]],
        }
        index_path = tmp_path / "index.json"
        index_path.write_text(json.dumps(index_data), encoding="utf-8")

        chunks, embeddings, model = _load_index(str(index_path))

        assert len(chunks) == 1
        assert isinstance(chunks[0], Chunk)
        assert chunks[0].title == "Title"
        assert chunks[0].content == "Some content"
        assert model == "test-model"
        assert embeddings.shape == (1, 3)
        assert embeddings[0, 0] == pytest.approx(0.1)

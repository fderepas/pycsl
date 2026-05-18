"""
Retriever — loads a pre-built vector index and finds relevant chunks.

Uses cosine similarity (via numpy) to rank chunks against a query embedding.
"""

import json
from pathlib import Path
from typing import List

import numpy as np

from skill2rag.chunker import Chunk
from skill2rag.embedder import embed


def _cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between a query vector and a matrix of vectors."""
    query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10
    matrix_norm = matrix / norms
    return matrix_norm @ query_norm


def _load_index(index_path: str) -> tuple:
    """Load the JSON index and return (chunks, embedding_matrix, model)."""
    data = json.loads(Path(index_path).read_text(encoding="utf-8"))
    chunks = [Chunk(**c) for c in data["chunks"]]
    embeddings = np.array(data["embeddings"], dtype=np.float32)
    model = data.get("model", "nomic-embed-text")
    return chunks, embeddings, model


def retrieve(
    query: str,
    index_path: str,
    top_k: int = 5,
    model: str | None = None,
) -> List[Chunk]:
    """Retrieve the most relevant skill chunks for a query.

    Args:
        query:       Natural language query.
        index_path:  Path to the JSON index built by build_index().
        top_k:       Number of chunks to return.
        model:       Embedding model override (default: model used at build time).

    Returns:
        List of Chunk objects, most relevant first.
    """
    chunks, embeddings, index_model = _load_index(index_path)
    model = model or index_model

    query_vec = np.array(embed(query, model), dtype=np.float32)
    scores = _cosine_similarity(query_vec, embeddings)

    top_indices = np.argsort(scores)[::-1][:top_k]
    return [chunks[i] for i in top_indices]


def retrieve_with_scores(
    query: str,
    index_path: str,
    top_k: int = 5,
    model: str | None = None,
) -> List[tuple[Chunk, float]]:
    """Like retrieve(), but also returns similarity scores."""
    chunks, embeddings, index_model = _load_index(index_path)
    model = model or index_model

    query_vec = np.array(embed(query, model), dtype=np.float32)
    scores = _cosine_similarity(query_vec, embeddings)

    top_indices = np.argsort(scores)[::-1][:top_k]
    return [(chunks[i], float(scores[i])) for i in top_indices]

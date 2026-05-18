"""
skill2rag — Hybrid RAG for LLM skills
======================================

Transforms large markdown skill documents into a searchable RAG index
using section-based chunking (markdown headings) and vector embeddings.

Public API:
    build_index(skill_dir, index_path, model)  — build/rebuild the vector index
    retrieve(query, index_path, top_k, model)  — retrieve relevant skill chunks
"""

from skill2rag.indexer import build_index
from skill2rag.retriever import retrieve, retrieve_with_scores

__all__ = ["build_index", "retrieve", "retrieve_with_scores"]

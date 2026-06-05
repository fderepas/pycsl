"""
Index builder — chunks skill files, embeds them, and stores the result.

The index is a single JSON file containing chunk metadata and their
embedding vectors, suitable for loading into memory at query time.
"""

import json
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import List

from skill2rag.chunker import Chunk, chunk_directory
from skill2rag.embedder import embed_batch


def _prepare_embed_text(chunk: Chunk) -> str:
    """Build the text that will be embedded for a chunk.

    Prepends the heading path so the embedding captures hierarchical context.
    """
    prefix = " > ".join(chunk.heading_path)
    return f"{prefix}\n\n{chunk.content}"


def build_index(
    skill_dir: str,
    index_path: str,
    model: str = "nomic-embed-text",
    batch_size: int = 16,
) -> None:
    """Build (or rebuild) the vector index from skill markdown files.

    Args:
        skill_dir:   Directory containing .md skill files.
        index_path:  Path where the JSON index will be written.
        model:       Embedding model name (passed to embedder).
        batch_size:  Number of chunks to embed per API call.
    """
    chunks = chunk_directory(skill_dir)
    if not chunks:
        print(f"No .md files found in {skill_dir}", file=sys.stderr)
        return

    print(f"Chunked {len(chunks)} sections from {skill_dir}", flush=True)

    # Embed in batches, with a live progress indicator.
    # `flush=True` is essential: when stdout is a pipe (not a TTY) Python
    # block-buffers it, so without an explicit flush the per-batch lines never
    # appear until the process exits — a slow/stuck Ollama embed then looks like
    # a total hang with no feedback. The "batch N/total" line is printed BEFORE
    # the (blocking) embed call, so you can see exactly which batch is stuck, and
    # the trailing "done in …s" surfaces a slow batch.
    texts = [_prepare_embed_text(c) for c in chunks]
    all_embeddings: List[List[float]] = []
    total_batches = (len(texts) + batch_size - 1) // batch_size
    t_start = time.monotonic()

    for bi, i in enumerate(range(0, len(texts), batch_size), start=1):
        batch = texts[i : i + batch_size]
        pct = bi * 100 // total_batches
        print(f"  Embedding batch {bi}/{total_batches} "
              f"({pct}%, {len(batch)} chunks)…", flush=True)
        t0 = time.monotonic()
        embs = embed_batch(batch, model)
        all_embeddings.extend(embs)
        print(f"    ✓ batch {bi}/{total_batches} in {time.monotonic() - t0:.1f}s "
              f"(elapsed {time.monotonic() - t_start:.0f}s)", flush=True)

    # Build index payload
    index_data = {
        "model": model,
        "chunks": [asdict(c) for c in chunks],
        "embeddings": all_embeddings,
    }

    out = Path(index_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index_data), encoding="utf-8")
    print(f"Index written to {index_path} ({len(chunks)} chunks, "
          f"{len(all_embeddings[0])}d vectors)", flush=True)

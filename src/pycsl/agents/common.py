"""Shared utilities for PyCSL agent scripts."""
from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path
from typing import Any, Union


def log(path: Union[str, Path], name: str, message: str) -> str:
    """Append a timestamped message to <path>/log/<name>.log."""
    log_dir = Path(path) / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{name}.log"
    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}")
    return str(log_file)


def retrieve_skill_chunks(
    index_path: Path,
    main_query: str,
    top_k: int = 10,
    project_root: Path | None = None,
    essential_queries: list[str] | None = None,
) -> str | None:
    """Retrieve relevant skill chunks via RAG.

    Runs each entry in *essential_queries* with top_k=3 to guarantee critical
    sections are always present, then runs *main_query* with the full *top_k*.
    Returns deduplicated chunks joined by ``---``, or None if the index is
    unavailable or skill2rag raises.
    """
    if not index_path.exists():
        return None
    try:
        if project_root:
            skill2rag_path = str(project_root / "src")
            if skill2rag_path not in sys.path:
                sys.path.insert(0, skill2rag_path)
        from skill2rag.retriever import retrieve  # noqa: E402

        seen_ids: set = set()
        chunks: list = []

        for query in (essential_queries or []):
            for chunk in retrieve(query=query, index_path=str(index_path), top_k=3):
                if chunk.chunk_id not in seen_ids:
                    seen_ids.add(chunk.chunk_id)
                    chunks.append(chunk)

        for chunk in retrieve(query=main_query, index_path=str(index_path), top_k=top_k):
            if chunk.chunk_id not in seen_ids:
                seen_ids.add(chunk.chunk_id)
                chunks.append(chunk)

        if not chunks:
            return None

        return "\n\n---\n\n".join(c.content for c in chunks)
    except Exception:
        return None


def extract_code_block(text: str, language: str = "python") -> str:
    """Extract code from a markdown fenced block.

    Falls back to a generic fence (no language tag), then returns *text*
    unchanged if no fence is found.
    """
    match = re.search(rf"```{language}\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1)
    match = re.search(r"```\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text


def load_config(config_path: Path) -> dict[str, Any]:
    """Load and return the JSON config at *config_path*.

    Raises RuntimeError with a clear message on missing file or bad JSON so
    callers don't need to handle low-level exceptions.
    """
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RuntimeError(f"Config file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse config {config_path}: {e}")

"""
Index freshness + coverage verifier.

Confirms the on-disk vector index reflects the current skill tree, WITHOUT
embedding anything (pure file-read + content-hash compare — no Ollama needed,
so it is fast and safe to run in CI).

Two questions are answered:

  * Coverage  — does every ``config/skills/<name>/SKILL.md`` contribute at
    least one chunk to the index? (A skill absent from the index cannot be
    retrieved.)
  * Freshness — does every chunk produced from the *current* tree appear in
    the index with a matching ``content_hash``? Drift is reported as:
        unindexed  current chunk_id not in the index   (new / never built)
        stale      chunk_id present but hash differs    (source edited since build)
        orphan     index chunk_id no longer in the tree (deleted / renamed)

``verify_index`` returns ``(ok, report)``; the CLI maps that to an exit code.
"""

from pathlib import Path
import json

from skill2rag.chunker import chunk_directory


def _index_source_files(index_chunks) -> set:
    return {c.get("source_file", "") for c in index_chunks}


def _skill_coverage(skill_dir: Path, index_sources: set) -> list:
    """Return the names of skill dirs that contribute NO chunk to the index.

    A skill is covered if its directory name (the ``source_file`` of its
    ``SKILL.md``) or any of its ``references/*.md`` stems is present in the
    index's source-file set.
    """
    missing = []
    for skill_md in sorted(skill_dir.glob("*/SKILL.md")):
        d = skill_md.parent
        stems = {d.name} | {f.stem for f in d.rglob("*.md")}
        if not (stems & index_sources):
            missing.append(d.name)
    return missing


def verify_index(skill_dir: str, index_path: str):
    """Compare the live skill tree against the built index.

    Returns ``(ok: bool, report: dict)``. ``report["index_missing"]`` is True
    (and ``ok`` is False) when the index file does not exist. ``orphan`` is a
    warning only and does not clear ``ok``.
    """
    idx = Path(index_path)
    if not idx.exists():
        return False, {"index_missing": True, "index_path": str(idx)}

    index_chunks = json.loads(idx.read_text(encoding="utf-8")).get("chunks", [])
    # chunk_id (= source::heading_path) is NOT unique — a file that repeats a
    # heading yields colliding ids — so freshness is compared on the SET of
    # (chunk_id, content_hash) PAIRS, not a {id: hash} map (which would collapse
    # duplicates and report false "stale").
    index_pairs = {(c["chunk_id"], c["content_hash"]) for c in index_chunks}
    index_ids = {c["chunk_id"] for c in index_chunks}
    index_sources = _index_source_files(index_chunks)

    current = chunk_directory(skill_dir)
    current_ids = {c.chunk_id for c in current}

    # unindexed: a chunk_id absent from the index entirely (new / never built).
    unindexed = sorted({c.chunk_id for c in current if c.chunk_id not in index_ids})
    # stale: chunk_id is in the index, but no indexed pair has this content_hash
    # (the source changed since the build). Deduped by chunk_id for reporting.
    stale = sorted({
        c.chunk_id for c in current
        if c.chunk_id in index_ids and (c.chunk_id, c.content_hash) not in index_pairs
    })
    orphan = sorted(cid for cid in index_ids if cid not in current_ids)
    missing_skills = _skill_coverage(Path(skill_dir), index_sources)

    report = {
        "index_missing": False,
        "index_path": str(idx),
        "skills_total": len(list(Path(skill_dir).glob("*/SKILL.md"))),
        "missing_skills": missing_skills,
        "current_chunks": len(current),
        "index_chunks": len(index_chunks),
        "unindexed": unindexed,
        "stale": stale,
        "orphan": orphan,
    }
    ok = not (missing_skills or unindexed or stale)
    return ok, report

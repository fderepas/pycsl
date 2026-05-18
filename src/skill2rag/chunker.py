"""
Markdown heading-based chunker.

Splits markdown files into structured chunks using H1/H2/H3 headings as
natural boundaries.  Each chunk preserves its full content (including code
blocks, tables, and nested structure).
"""

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class Chunk:
    """A single retrievable section of a skill document."""
    chunk_id: str
    source_file: str
    heading_path: List[str]
    title: str
    content: str
    content_hash: str
    level: int

    def display_path(self) -> str:
        return " > ".join(self.heading_path) if self.heading_path else self.source_file


_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


def _make_chunk_id(source_file: str, heading_path: List[str]) -> str:
    key = source_file + "::" + "::".join(heading_path)
    return key


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def chunk_file(filepath: str | Path) -> List[Chunk]:
    """Split a single markdown file into heading-based chunks.

    Returns one Chunk per top-level or nested section.  Content that appears
    before the first heading is assigned a chunk titled after the filename.
    """
    filepath = Path(filepath)
    text = filepath.read_text(encoding="utf-8")

    # Strip optional YAML frontmatter before chunking
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            text = text[end + 5:]

    # Use parent directory name as source when the file is named SKILL.md
    if filepath.stem.upper() == "SKILL":
        source = filepath.parent.name
    else:
        source = filepath.stem

    # Find all headings with their positions
    headings = [(m.start(), len(m.group(1)), m.group(2).strip()) for m in _HEADING_RE.finditer(text)]

    if not headings:
        # No headings — whole file is one chunk
        return [
            Chunk(
                chunk_id=_make_chunk_id(source, [source]),
                source_file=source,
                heading_path=[source],
                title=source,
                content=text.strip(),
                content_hash=_content_hash(text),
                level=0,
            )
        ]

    chunks: List[Chunk] = []

    # Content before first heading
    preamble = text[: headings[0][0]].strip()
    if preamble:
        chunks.append(
            Chunk(
                chunk_id=_make_chunk_id(source, [source]),
                source_file=source,
                heading_path=[source],
                title=source,
                content=preamble,
                content_hash=_content_hash(preamble),
                level=0,
            )
        )

    # Build heading stack for hierarchy tracking
    heading_stack: List[str] = []

    for idx, (pos, level, title) in enumerate(headings):
        # Determine content end
        if idx + 1 < len(headings):
            content_end = headings[idx + 1][0]
        else:
            content_end = len(text)

        content = text[pos:content_end].strip()

        # Update heading stack: pop headings at same or deeper level
        while len(heading_stack) >= level:
            heading_stack.pop()
        heading_stack.append(title)
        heading_path = list(heading_stack)

        chunks.append(
            Chunk(
                chunk_id=_make_chunk_id(source, heading_path),
                source_file=source,
                heading_path=heading_path,
                title=title,
                content=content,
                content_hash=_content_hash(content),
                level=level,
            )
        )

    return chunks


def chunk_directory(skill_dir: str | Path) -> List[Chunk]:
    """Chunk all .md files in a directory (recursively).

    Supports both flat layouts (``skills/*.md``) and the SKILL.md convention
    (``skills/<name>/SKILL.md``).
    """
    skill_dir = Path(skill_dir)
    all_chunks: List[Chunk] = []
    for md_file in sorted(skill_dir.rglob("*.md")):
        all_chunks.extend(chunk_file(md_file))
    return all_chunks

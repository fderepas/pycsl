"""Unit tests for skill2rag.chunker."""

import hashlib
from pathlib import Path

import pytest

from skill2rag.chunker import (
    Chunk,
    _content_hash,
    _make_chunk_id,
    chunk_directory,
    chunk_file,
)


@pytest.fixture
def tmp_md(tmp_path):
    """Helper: write markdown to a temp file and return its path."""
    def _write(content: str, name: str = "test.md") -> Path:
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return p
    return _write


@pytest.fixture
def tmp_skill(tmp_path):
    """Helper: write a SKILL.md inside a named subdirectory."""
    def _write(content: str, skill_name: str) -> Path:
        d = tmp_path / skill_name
        d.mkdir()
        p = d / "SKILL.md"
        p.write_text(content, encoding="utf-8")
        return p
    return _write


# --- _content_hash ---

class TestContentHash:
    def test_deterministic(self):
        assert _content_hash("hello") == _content_hash("hello")

    def test_different_input_different_hash(self):
        assert _content_hash("hello") != _content_hash("world")

    def test_is_hex_prefix(self):
        h = _content_hash("test")
        assert len(h) == 16
        int(h, 16)  # should not raise


# --- _make_chunk_id ---

class TestMakeChunkId:
    def test_basic(self):
        assert _make_chunk_id("myfile", ["A", "B"]) == "myfile::A::B"

    def test_single_heading(self):
        assert _make_chunk_id("src", ["Title"]) == "src::Title"


# --- Chunk.display_path ---

class TestChunkDisplayPath:
    def test_joins_heading_path(self):
        c = Chunk("id", "src", ["A", "B", "C"], "C", "", "", 3)
        assert c.display_path() == "A > B > C"

    def test_empty_heading_path_falls_back(self):
        c = Chunk("id", "src", [], "t", "", "", 0)
        assert c.display_path() == "src"


# --- chunk_file ---

class TestChunkFile:
    def test_no_headings_single_chunk(self, tmp_md):
        p = tmp_md("Just some plain text.\nNo headings here.")
        chunks = chunk_file(p)
        assert len(chunks) == 1
        assert chunks[0].title == "test"
        assert chunks[0].level == 0
        assert "plain text" in chunks[0].content

    def test_single_h1(self, tmp_md):
        p = tmp_md("# Title\n\nBody text here.")
        chunks = chunk_file(p)
        assert len(chunks) == 1
        assert chunks[0].title == "Title"
        assert chunks[0].level == 1
        assert "Body text here" in chunks[0].content

    def test_h1_h2_hierarchy(self, tmp_md):
        md = "# Top\n\nIntro\n\n## Sub\n\nDetails"
        p = tmp_md(md)
        chunks = chunk_file(p)
        assert len(chunks) == 2
        assert chunks[0].heading_path == ["Top"]
        assert chunks[1].heading_path == ["Top", "Sub"]
        assert chunks[1].level == 2

    def test_h1_h2_h3_hierarchy(self, tmp_md):
        md = "# A\n\n## B\n\n### C\n\nDeep"
        p = tmp_md(md)
        chunks = chunk_file(p)
        assert len(chunks) == 3
        assert chunks[2].heading_path == ["A", "B", "C"]
        assert chunks[2].level == 3

    def test_preamble_before_first_heading(self, tmp_md):
        md = "Some preamble text.\n\n# Heading\n\nBody"
        p = tmp_md(md)
        chunks = chunk_file(p)
        assert len(chunks) == 2
        assert chunks[0].title == "test"  # filename stem
        assert chunks[0].level == 0
        assert "preamble" in chunks[0].content
        assert chunks[1].title == "Heading"

    def test_yaml_frontmatter_stripped(self, tmp_md):
        md = "---\nname: my-skill\ndescription: A test\n---\n\n# Title\n\nContent"
        p = tmp_md(md)
        chunks = chunk_file(p)
        assert len(chunks) == 1
        assert chunks[0].title == "Title"
        # Frontmatter should not appear in any chunk
        for c in chunks:
            assert "name: my-skill" not in c.content
            assert "---" not in c.content.split("\n")[0]

    def test_skill_md_uses_parent_dir_name(self, tmp_skill):
        p = tmp_skill("# Hello\n\nWorld", "my-skill")
        chunks = chunk_file(p)
        assert chunks[0].source_file == "my-skill"

    def test_regular_md_uses_stem(self, tmp_md):
        p = tmp_md("# Hello\n\nWorld", "guide.md")
        chunks = chunk_file(p)
        assert chunks[0].source_file == "guide"

    def test_content_hash_populated(self, tmp_md):
        p = tmp_md("# H\n\nText")
        chunks = chunk_file(p)
        assert chunks[0].content_hash
        assert len(chunks[0].content_hash) == 16

    def test_sibling_headings_reset_stack(self, tmp_md):
        md = "# A\n\n## B1\n\ntext\n\n## B2\n\ntext"
        p = tmp_md(md)
        chunks = chunk_file(p)
        assert chunks[1].heading_path == ["A", "B1"]
        assert chunks[2].heading_path == ["A", "B2"]


# --- chunk_directory ---

class TestChunkDirectory:
    def test_recursive_discovery(self, tmp_path):
        # Flat file
        (tmp_path / "flat.md").write_text("# Flat\n\nContent", encoding="utf-8")
        # Nested SKILL.md
        sub = tmp_path / "nested"
        sub.mkdir()
        (sub / "SKILL.md").write_text("# Nested\n\nContent", encoding="utf-8")

        chunks = chunk_directory(tmp_path)
        sources = {c.source_file for c in chunks}
        assert "flat" in sources
        assert "nested" in sources

    def test_empty_directory(self, tmp_path):
        chunks = chunk_directory(tmp_path)
        assert chunks == []

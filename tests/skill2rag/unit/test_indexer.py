"""Unit tests for skill2rag.indexer."""

from skill2rag.chunker import Chunk
from skill2rag.indexer import _prepare_embed_text


class TestPrepareEmbedText:
    def test_prepends_heading_path(self):
        chunk = Chunk(
            chunk_id="src::A::B",
            source_file="src",
            heading_path=["A", "B"],
            title="B",
            content="# B\n\nSome body text",
            content_hash="abc",
            level=2,
        )
        result = _prepare_embed_text(chunk)
        assert result.startswith("A > B\n\n")
        assert "Some body text" in result

    def test_single_heading(self):
        chunk = Chunk(
            chunk_id="f::Top",
            source_file="f",
            heading_path=["Top"],
            title="Top",
            content="# Top\n\nContent",
            content_hash="def",
            level=1,
        )
        result = _prepare_embed_text(chunk)
        assert result.startswith("Top\n\n")

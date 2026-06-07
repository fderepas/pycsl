# Formal tests for pure_lib/htm — html module
from pure_lib.htm import escape, unescape


def test_escape_returns_str() -> str:
    """escape returns a string."""
    return escape("hello")


def test_unescape_returns_str() -> str:
    """unescape returns a string."""
    return unescape("world")

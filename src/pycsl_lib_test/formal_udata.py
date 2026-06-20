# Formal tests for pycsl_lib/udata — unicodedata module
from pycsl_lib.udata import lookup, normalize


def test_lookup_returns_str() -> str:
    """lookup returns a string."""
    return lookup("LATIN SMALL LETTER A")


def test_normalize_returns_str() -> str:
    """normalize returns a string."""
    return normalize("NFC", "hello")

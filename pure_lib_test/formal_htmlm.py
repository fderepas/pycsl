# Formal test for html (htmlm) module
#
# Based on library_reference/html.rst:
#   "Convert the characters &, < and > in string s to HTML-safe sequences."
#   → escaping replaces 1-char entities with multi-char, so result >= input.
#   "Convert all named and numeric character references to Unicode."
#   → unescaping replaces multi-char refs with 1-char, so result <= input.
#
# Tests exercise the strengthened contracts:
#   - escape: result >= s (escaping only grows)
#   - unescape: result <= s (unescaping only shrinks)
#   - escape_quote: result >= s (same growth property)

from pure_lib.htmlm import escape, unescape, escape_quote


#@ ensures \result >= 42
def test_escape_grows() -> int:
    """Escaping grows or preserves: result >= input."""
    return escape(42)


#@ ensures \result >= 0 and \result <= 100
def test_unescape_shrinks() -> int:
    """Unescaping shrinks or preserves: result <= input."""
    return unescape(100)


#@ ensures \result >= 50
def test_escape_quote_grows() -> int:
    """escape_quote grows or preserves: result >= input."""
    return escape_quote(50)

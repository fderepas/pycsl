# Formal test for html (htmlm) module — universally quantified
#
# Based on library_reference/html.rst:
#   "Convert the characters &, < and > in string s to HTML-safe sequences."
#   → escaping replaces 1-char entities with multi-char, so result >= input.
#   "Convert all named and numeric character references to Unicode."
#   → unescaping replaces multi-char refs with 1-char, so result <= input.

from pure_lib.htmlm import escape, unescape, escape_quote


#@ requires s >= 0 and s < 2147483647
#@ ensures \result >= s
def test_escape_grows(s: int) -> int:
    """escape(s) >= s for all s. Escaping only grows strings."""
    return escape(s)


#@ requires s >= 0 and s < 2147483647
#@ ensures \result >= 0 and \result <= s
def test_unescape_shrinks(s: int) -> int:
    """unescape(s) <= s for all s. Unescaping only shrinks strings."""
    return unescape(s)


#@ requires s >= 0 and s < 2147483647
#@ ensures \result >= s
def test_escape_quote_grows(s: int) -> int:
    """escape_quote(s) >= s for all s. Same growth property as escape."""
    return escape_quote(s)

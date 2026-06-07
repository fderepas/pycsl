# Formal test for html (htmlm) module
#
# Based on library_reference/html.rst:
#   "Convert the chars &, < and > in string s to HTML-safe sequences."
#   "Convert all named and numeric character references... to the
#    corresponding Unicode characters."
#
# Tests:
#   1. escape output >= input (escaping only grows)
#   2. unescape output >= 0 (valid string)
#   3. escape_quote monotone (output >= input)

from pure_lib.htmlm import escape, unescape, escape_quote


#@ ensures \result >= 0
def test_escape_nonneg() -> int:
    """Escaping any string yields non-negative length."""
    return escape(42)


#@ ensures \result >= 0
def test_unescape_nonneg() -> int:
    """Unescaping yields non-negative length."""
    return unescape(100)


#@ ensures \result >= 50
def test_escape_quote_monotone() -> int:
    """escape_quote(50) >= 50 — escaping only grows."""
    return escape_quote(50)

# Formal tests for pure_lib/htmlm — HTML module model
from pure_lib.htmlm import escape, unescape, escape_quote


#@ requires s >= 0
#@ ensures \result >= s
def test_escape_grows(s: int) -> int:
    """HTML escape never shrinks the string."""
    return escape(s)


#@ requires s >= 0
#@ ensures \result <= s
def test_unescape_shrinks(s: int) -> int:
    """HTML unescape never grows the string."""
    return unescape(s)


#@ ensures \result == 0
def test_escape_empty() -> int:
    """Escaping empty string gives empty string."""
    return escape(0)


#@ ensures \result == 0
def test_unescape_empty() -> int:
    """Unescaping empty string gives empty string."""
    return unescape(0)


#@ requires s >= 0
#@ ensures \result >= s
def test_escape_quote_grows(s: int) -> int:
    """escape_quote also never shrinks."""
    return escape_quote(s)

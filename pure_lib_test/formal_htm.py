# Formal tests for pure_lib/htm — html module
from pure_lib.htm import escape, unescape


#@ requires length >= 0
#@ ensures \result >= length
def test_escape_grows(length: int) -> int:
    """Escaping never shrinks text."""
    return escape(length)


#@ requires length >= 0
#@ ensures \result <= length
def test_unescape_shrinks(length: int) -> int:
    """Unescaping never grows text."""
    return unescape(length)

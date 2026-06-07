# Formal test for textwrap (txtwrp) module
#
# Based on library_reference/textwrap.rst:
#   "Returns a list of output lines" → empty text → empty list (0 lines).
#   "so every line is at most width characters long" → non-empty text → >= 1 line.
#   "Collapse and truncate to fit in width" → result <= width AND <= text.
#   "Remove any common leading whitespace" → result <= text.
#   "Add prefix to the beginning of selected lines" → result >= text.

from pure_lib.txtwrp import wrap, fill, shorten, dedent, indent


#@ ensures \result == 0
def test_wrap_empty() -> int:
    """Empty text → empty list (0 lines). Direct from RST."""
    return wrap(0, 80)


#@ ensures \result >= 1
def test_wrap_nonempty() -> int:
    """Non-empty text → at least 1 line. Direct from RST."""
    return wrap(40, 80)


#@ ensures \result == 0
def test_fill_empty() -> int:
    """Empty text → empty string. fill = join(wrap(text))."""
    return fill(0, 80)


#@ ensures \result >= 0 and \result <= 200 and \result <= 80
def test_shorten_bounded() -> int:
    """shorten(200, 80): result <= text AND <= width."""
    return shorten(200, 80)


#@ ensures \result >= 0 and \result <= 100
def test_dedent_bounded() -> int:
    """dedent(100) removes whitespace: result <= original."""
    return dedent(100)


#@ ensures \result >= 50
def test_indent_grows() -> int:
    """indent(50, 4): result >= original (prefix added)."""
    return indent(50, 4)

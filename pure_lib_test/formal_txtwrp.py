# Formal test for textwrap (txtwrp) module
#
# Based on library_reference/textwrap.rst:
#   "Wraps the single paragraph in text... Returns a list of output lines."
#   "Remove any common leading whitespace from all lines in text."
#   "Add prefix to the beginning of selected lines in text."
#
# Tests verify contract postconditions only:
#   - wrap: ensures result >= 0
#   - shorten: ensures 0 <= result <= text
#   - dedent: ensures 0 <= result <= text
#   - indent: ensures result >= text

from pure_lib.txtwrp import wrap, fill, shorten, dedent, indent


#@ ensures \result >= 0
def test_wrap_nonneg() -> int:
    """wrap always returns non-negative line count."""
    return wrap(40, 80)


#@ ensures \result >= 0
def test_fill_nonneg() -> int:
    """fill returns non-negative length."""
    return fill(100, 80)


#@ ensures \result >= 0 and \result <= 200
def test_shorten_bounded() -> int:
    """shorten(200, 80) is in [0, 200]."""
    return shorten(200, 80)


#@ ensures \result >= 0 and \result <= 100
def test_dedent_bounded() -> int:
    """dedent(100) is in [0, 100]."""
    return dedent(100)


#@ ensures \result >= 50
def test_indent_grows() -> int:
    """indent(50, 4) >= 50."""
    return indent(50, 4)

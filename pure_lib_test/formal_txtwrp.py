# Formal test for textwrap (txtwrp) module — universally quantified
#
# Based on library_reference/textwrap.rst:
#   "Returns a list of output lines" → empty text → empty list (0 lines).
#   "so every line is at most width characters long" → non-empty text → >= 1 line.
#   "Collapse and truncate to fit in width" → result <= width AND <= text.
#   "Remove any common leading whitespace" → result <= text.
#   "Add prefix to the beginning of selected lines" → result >= text.

from pure_lib.txtwrp import wrap, fill, shorten, dedent, indent


#@ requires width > 0 and width < 2147483647
#@ ensures \result == 0
def test_wrap_empty(width: int) -> int:
    """wrap(0, width) == 0 for all widths. Empty text → empty list."""
    return wrap(0, width)


#@ requires text > 0 and text < 2147483647
#@ requires width > 0 and width < 2147483647
#@ ensures \result >= 1
#@ ensures \result == (text + width - 1) // width
def test_wrap_nonempty(text: int, width: int) -> int:
    """wrap(text, width) == ceil(text/width) for all text > 0. Exact formula."""
    return wrap(text, width)


#@ requires width > 0 and width < 2147483647
#@ ensures \result == 0
def test_fill_empty(width: int) -> int:
    """fill(0, width) == 0 for all widths. Empty text → empty string."""
    return fill(0, width)


#@ requires text >= 0 and text < 2147483647
#@ requires width > 0 and width < 2147483647
#@ ensures \result >= 0 and \result <= text and \result <= width
#@ ensures text <= width ==> \result == text
#@ ensures text > width ==> \result == width
def test_shorten_bounded(text: int, width: int) -> int:
    """shorten(text, width) == min(text, width) for all inputs. Exact."""
    return shorten(text, width)


#@ requires text >= 0 and text < 2147483647
#@ ensures \result >= 0 and \result <= text
def test_dedent_bounded(text: int) -> int:
    """dedent(text) <= text for all text. Whitespace only removed."""
    return dedent(text)


#@ requires text >= 0 and text < 2147483647
#@ requires prefix >= 0 and prefix < 2147483647
#@ ensures \result >= text
#@ ensures \result == text + prefix
def test_indent_grows(text: int, prefix: int) -> int:
    """indent(text, prefix) == text + prefix for all inputs. Exact."""
    return indent(text, prefix)

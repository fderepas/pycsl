# Formal test for string (strmod) module
#
# Based on library_reference/string.rst:
#   "Split into words, capitalize each word, and join."
#   → split+join removes duplicate whitespace → result <= input.
#   → empty input → empty output.
#   "The substitute() method substitutes $-variables."

from pure_lib.strmod import capwords, template_substitute, template_safe_substitute, format_field


#@ ensures \result >= 0 and \result <= 20
def test_capwords_bounded() -> int:
    """capwords(20) in [0, 20]: RST says split+capitalize+join."""
    return capwords(20)


#@ ensures \result == 0
def test_capwords_empty() -> int:
    """capwords(0) == 0: empty input → empty output."""
    return capwords(0)


#@ ensures \result >= 0
def test_template_sub_nonneg() -> int:
    """substitute result is non-negative."""
    return template_substitute(10, 5)


#@ ensures \result >= 10
def test_safe_sub_grows() -> int:
    """safe_substitute(10, 5) >= 10: unresolved vars stay, so >= template."""
    return template_safe_substitute(10, 5)


#@ ensures \result >= 0
def test_format_field_nonneg() -> int:
    """format_field result is non-negative."""
    return format_field(3, 7)

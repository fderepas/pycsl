# Formal test for string (strmod) module
#
# Based on library_reference/string.rst:
#   "Split the argument into words, capitalize each word, and join."
#   "The substitute() method... substitutes $-variables."
#
# Tests verify contract postconditions:
#   - capwords: ensures 0 <= result <= s
#   - template_substitute: ensures result >= 0
#   - format_field: ensures result >= 0

from pure_lib.strmod import capwords, template_substitute, format_field


#@ ensures \result >= 0 and \result <= 20
def test_capwords_bounded() -> int:
    """capwords(20) in [0, 20]: capitalize doesn't grow."""
    return capwords(20)


#@ ensures \result >= 0
def test_template_sub_nonneg() -> int:
    """substitute result is non-negative."""
    return template_substitute(10, 5)


#@ ensures \result >= 0
def test_format_field_nonneg() -> int:
    """format_field result is non-negative."""
    return format_field(3, 7)

# Formal test for string (strmod) module — universally quantified
#
# Based on library_reference/string.rst:
#   "Split the argument into words using str.split(), capitalize each word
#    using str.capitalize(), and join the capitalized words using str.join()."
#   → split+join removes duplicate whitespace → result <= input.
#   → empty input → empty output.
#   "The substitute() method substitutes $-variables."

from pure_lib.strmod import capwords, template_substitute, template_safe_substitute, format_field


#@ requires s >= 0 and s < 2147483647
#@ ensures \result >= 0 and \result <= s
def test_capwords_bounded(s: int) -> int:
    """capwords(s) <= s for all s. Split+join only removes whitespace."""
    return capwords(s)


#@ ensures \result == 0
def test_capwords_empty() -> int:
    """capwords(0) == 0. Empty input → empty output. (Single fixed input.)"""
    return capwords(0)


#@ requires template >= 0 and template < 2147483647
#@ requires mapping >= 0 and mapping < 2147483647
#@ ensures \result >= 0
#@ ensures \result == template + mapping
def test_template_sub_nonneg(template: int, mapping: int) -> int:
    """template_substitute(template, mapping) == template + mapping. Exact."""
    return template_substitute(template, mapping)


#@ requires template >= 0 and template < 2147483647
#@ requires mapping >= 0 and mapping < 2147483647
#@ ensures \result >= template
#@ ensures \result == template + mapping
def test_safe_sub_grows(template: int, mapping: int) -> int:
    """safe_substitute(template, mapping) == template + mapping. Exact."""
    return template_safe_substitute(template, mapping)


#@ requires fmt >= 0 and fmt < 2147483647
#@ requires val >= 0 and val < 2147483647
#@ ensures \result >= 0
#@ ensures fmt == 0 ==> \result == val
#@ ensures fmt > 0 ==> \result == fmt + val
def test_format_field_nonneg(fmt: int, val: int) -> int:
    """format_field exact: fmt==0 → val, fmt>0 → fmt+val."""
    return format_field(fmt, val)

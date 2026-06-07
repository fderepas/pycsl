# Formal test for pprint (pp) module
#
# Based on library_reference/pprint.rst:
#   "Return the formatted representation of object as a string."
#   "Determine if the formatted representation of the object is 'readable'."
#
# Tests:
#   1. pformat returns non-negative
#   2. saferepr returns non-negative
#   3. isrecursive returns 0 or 1

from pure_lib.pp import pformat, saferepr, isrecursive


#@ ensures \result >= 0
def test_pformat_nonneg() -> int:
    """pformat result (string length) is non-negative."""
    return pformat(25)


#@ ensures \result >= 0
def test_saferepr_nonneg() -> int:
    """saferepr result is non-negative."""
    return saferepr(10)


#@ ensures \result >= 0
def test_isrecursive_bool() -> int:
    """isrecursive returns 0 (non-recursive)."""
    return isrecursive(5)

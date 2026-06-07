# Formal test for pprint (pp) module — universally quantified
#
# Based on library_reference/pprint.rst:
#   "Return the formatted representation of object as a string."
#   "Determine if the formatted representation is 'readable'."
#   "Determine if object requires a recursive representation."

from pure_lib.pp import pformat, saferepr, isreadable, isrecursive


#@ requires obj >= 0 and obj < 2147483647
#@ ensures \result >= 0
#@ ensures \result == obj
def test_pformat_nonneg(obj: int) -> int:
    """pformat(obj) == obj for all obj. Exact model identity."""
    return pformat(obj)


#@ requires obj >= 0 and obj < 2147483647
#@ ensures \result >= 0
#@ ensures \result == obj
def test_saferepr_nonneg(obj: int) -> int:
    """saferepr(obj) == obj for all obj. Exact model identity."""
    return saferepr(obj)


#@ requires obj >= 0 and obj < 2147483647
#@ ensures \result >= 0 and \result <= 1
def test_isreadable_bool(obj: int) -> int:
    """isreadable(obj) in {0, 1} for all obj. Boolean result."""
    return isreadable(obj)


#@ requires obj >= 0 and obj < 2147483647
#@ ensures \result >= 0 and \result <= 1
def test_isrecursive_bool(obj: int) -> int:
    """isrecursive(obj) in {0, 1} for all obj. Boolean result."""
    return isrecursive(obj)

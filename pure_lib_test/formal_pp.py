# Formal test for pprint (pp) module
#
# Based on library_reference/pprint.rst:
#   "Return the formatted representation of object as a string."
#   "Determine if the formatted representation is 'readable'."
#   "Determine if object requires a recursive representation."

from pure_lib.pp import pformat, saferepr, isreadable, isrecursive


#@ ensures \result >= 0
def test_pformat_nonneg() -> int:
    """RST: 'Return the formatted representation as a string.' Length >= 0."""
    return pformat(25)


#@ ensures \result >= 0
def test_saferepr_nonneg() -> int:
    """RST: 'Version of repr() with limits.' Length >= 0."""
    return saferepr(10)


#@ ensures \result >= 0 and \result <= 1
def test_isreadable_bool() -> int:
    """RST: 'Determine if readable.' Returns 0 or 1."""
    return isreadable(5)


#@ ensures \result >= 0 and \result <= 1
def test_isrecursive_bool() -> int:
    """RST: 'Determine if object requires recursive representation.' 0 or 1."""
    return isrecursive(5)

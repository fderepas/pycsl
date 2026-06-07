# Formal test for abc (abcmod) module
#
# Based on library_reference/abc.rst:
#   "A decorator indicating abstract methods... abstractmethod() may be used
#    to declare abstract methods for properties and descriptors."
#
# Tests:
#   1. abstractmethod is identity (returns its argument)
#   2. update_abstractmethods is identity

from pure_lib.abcmod import abstractmethod, update_abstractmethods


#@ ensures \result == 42
def test_abstractmethod_identity() -> int:
    """abstractmethod(42) == 42: decorator returns function unchanged."""
    return abstractmethod(42)


#@ ensures \result == 7
def test_update_abstractmethods_identity() -> int:
    """update_abstractmethods(7) == 7: class unchanged."""
    return update_abstractmethods(7)

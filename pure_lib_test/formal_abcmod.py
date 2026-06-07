# Formal test for abc (abcmod) module
#
# Based on library_reference/abc.rst:
#   "A decorator indicating abstract methods."
#   "Returns cls, to allow usage as a class decorator."

from pure_lib.abcmod import abstractmethod, update_abstractmethods


#@ ensures \result == 42
def test_abstractmethod_identity() -> int:
    """RST: decorator returns function unchanged. abstractmethod(42) == 42."""
    return abstractmethod(42)


#@ ensures \result == 7
def test_update_identity() -> int:
    """RST: 'Returns cls.' update_abstractmethods(7) == 7."""
    return update_abstractmethods(7)

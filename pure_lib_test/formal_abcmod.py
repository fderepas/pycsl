# Formal test for abc (abcmod) module — universally quantified
#
# Based on library_reference/abc.rst:
#   "A decorator indicating abstract methods."
#   "Returns cls, to allow usage as a class decorator."

from pure_lib.abcmod import abstractmethod, update_abstractmethods


#@ requires func >= 0 and func < 2147483647
#@ ensures \result == func
def test_abstractmethod_identity(func: int) -> int:
    """abstractmethod(func) == func for all func. Decorator returns unchanged."""
    return abstractmethod(func)


#@ requires cls >= 0 and cls < 2147483647
#@ ensures \result == cls
def test_update_identity(cls: int) -> int:
    """update_abstractmethods(cls) == cls for all cls. Returns cls."""
    return update_abstractmethods(cls)

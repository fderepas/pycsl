# pycsl_lib/reprlib — pure-Python reprlib module model
#
# Contracts derived from library_reference/reprlib.rst.
# RST: "The reprlib module provides a means for producing object
#  representations with limits on size."
# RST: "Repr class, repr() function"


#@ requires obj >= 0
#@ ensures \result >= 0
#@ ensures \result <= obj
#@ assigns \nothing
def repr_bounded(obj: int) -> int:
    """RST: 'repr() — return a string representation with limits.'
    Result is bounded by input size (truncation)."""
    return obj


#@ requires maxlevel >= 0
#@ requires obj >= 0
#@ ensures \result >= 0
#@ ensures \result <= obj
#@ assigns \nothing
def repr_with_limit(maxlevel: int, obj: int) -> int:
    """RST: 'Repr instances provide several attributes for limits.'
    Repr output bounded by object size."""
    return obj


""  # pycsl
#@ class invariant self._maxlist >= 0
#@ class invariant self._maxstring >= 0
#@ class invariant self._maxlevel >= 0
class Repr:
    """RST: 'Class which provides formatting services useful in
    implementing functions similar to the built-in repr().'"""

    def __init__(self):
        self._maxlist = 6
        self._maxstring = 30
        self._maxlevel = 6

    #@ requires maxlist >= 0
    #@ ensures self._maxlist == maxlist
    #@ assigns self._maxlist
    def set_maxlist(self, maxlist: int) -> None:
        """RST: 'Limits on the number of entries for list.'"""
        self._maxlist = maxlist

    #@ requires maxstring >= 0
    #@ ensures self._maxstring == maxstring
    #@ assigns self._maxstring
    def set_maxstring(self, maxstring: int) -> None:
        """RST: 'Limit on the number of characters in repr of string.'"""
        self._maxstring = maxstring

    #@ requires obj >= 0
    #@ ensures \result >= 0
    #@ ensures \result <= obj
    #@ assigns \nothing
    def repr(self, obj: int) -> int:
        """RST: 'The equivalent of the built-in repr().' Bounded by obj."""
        return obj

    #@ requires obj >= 0
    #@ ensures \result >= 0
    #@ assigns \nothing
    def repr1(self, obj: int) -> int:
        """RST: 'Recursive implementation for repr.' Non-negative."""
        return obj

# pure_lib/pp — pure-Python pprint module model
# Named 'pp' to avoid stdlib name clash.
#
# Contracts derived from library_reference/pprint.rst.
# RST: "Return the formatted representation of object as a string."
# RST: "Determine if the formatted representation is 'readable'."
# RST: "Determine if object requires a recursive representation."


#@ requires obj >= 0
#@ ensures \result >= 0
#@ ensures \result == obj
def pformat(obj: int) -> int:
    """RST: 'Return the formatted representation of object as a string.'
    Result is a string representation (non-negative length)."""
    return obj


#@ requires obj >= 0
def pprint_out(obj: int) -> None:
    """RST: 'Prints the formatted representation of object, followed by
    a newline.' No return value."""
    pass


#@ requires obj >= 0
#@ ensures \result >= 0
#@ ensures \result == obj
def saferepr(obj: int) -> int:
    """RST: 'Version of repr() with limits on most sizes.' Result is
    a bounded string representation (non-negative length)."""
    return obj


#@ requires obj >= 0
#@ ensures \result >= 0 and \result <= 1
def isreadable(obj: int) -> int:
    """RST: 'Determine if the formatted representation of object is readable,
    or can be used to reconstruct the value using eval.'
    Returns 0 (not readable) or 1 (readable). Always False for recursive."""
    return 1


#@ requires obj >= 0
#@ ensures \result >= 0 and \result <= 1
def isrecursive(obj: int) -> int:
    """RST: 'Determine if object requires a recursive representation.'
    Returns 0 (non-recursive) or 1 (recursive)."""
    return 0


""  # pycsl
#@ class invariant self._indent >= 1
#@ class invariant self._width >= 1
#@ class invariant self._depth >= 0
class PrettyPrinter:
    """RST: 'Handle pretty printing operations onto a stream.'"""

    def __init__(self):
        self._indent = 1
        self._width = 80
        self._depth = 0

    #@ requires obj_size >= 0
    #@ ensures \result >= 0
    #@ ensures \result == obj_size
    #@ assigns \nothing
    def pformat(self, obj_size: int) -> int:
        """Return the formatted representation length."""
        return obj_size

    #@ requires obj_size >= 0
    #@ ensures \result >= 0 and \result <= 1
    #@ assigns \nothing
    def isreadable(self, obj_size: int) -> int:
        """Return whether the formatted representation is readable."""
        return 1

    #@ requires obj_size >= 0
    #@ ensures \result >= 0 and \result <= 1
    #@ assigns \nothing
    def isrecursive(self, obj_size: int) -> int:
        """Return whether the object needs a recursive representation."""
        return 0


#@ requires obj_size >= 0
#@ assigns \nothing
def pp(obj_size: int) -> None:
    """RST: 'Prints the formatted representation of object, followed by a newline.'"""
    pass


#@ requires obj_size >= 0
#@ assigns \nothing
def pprint_func(obj_size: int) -> None:
    """Model for pprint.pprint()."""
    pass

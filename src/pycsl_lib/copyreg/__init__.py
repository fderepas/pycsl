# pycsl_lib/copyreg — pure-Python copyreg module model
#
# Contracts derived from library_reference/copyreg.rst.
# RST: "The copyreg module offers a way to define functions used while
#  pickling specific objects."
# RST: "pickle(), constructor(), dispatch_table"
#
# Model: registration count tracking.


""  # pycsl
#@ class invariant self._count >= 0
class Registry:
    """Model of the copyreg dispatch table."""

    def __init__(self):
        self._count = 0

    #@ requires obj_type >= 0
    #@ requires func >= 0
    #@ ensures self._count == \old(self._count) + 1
    #@ assigns self._count
    def pickle(self, obj_type: int, func: int) -> None:
        """RST: 'Declares that func should be used as a reduction function
        for objects of type obj_type.'"""
        self._count = self._count + 1

    #@ requires func >= 0
    #@ ensures self._count == \old(self._count) + 1
    #@ assigns self._count
    def constructor(self, func: int) -> None:
        """RST: 'Declares func to be a valid constructor.'"""
        self._count = self._count + 1

    #@ ensures \result == self._count
    #@ assigns \nothing
    def size(self) -> int:
        """Number of registered reducers."""
        return self._count


#@ requires obj_type >= 0
#@ requires func >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def pickle(obj_type: int, func: int) -> int:
    """RST: 'Declares that func should be used as a reduction function.'
    Returns registration id."""
    return obj_type


#@ requires func >= 0
#@ ensures \result == func
#@ assigns \nothing
def constructor(func: int) -> int:
    """RST: 'Declares func to be a valid constructor.'"""
    return func

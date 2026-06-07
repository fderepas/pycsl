# pure_lib/abcmod — pure-Python abc module model
# Named 'abcmod' to avoid stdlib name clash.
#
# Contracts derived from library_reference/abc.rst.
# RST: "A decorator indicating abstract methods."
# RST: "Returns cls, to allow usage as a class decorator."


#@ requires func >= 0
#@ ensures \result == func
def abstractmethod(func: int) -> int:
    """RST: 'A decorator indicating abstract methods.'
    Returns the function unchanged (it is just marked)."""
    return func


#@ requires func >= 0
#@ ensures \result == func
def abstractclassmethod(func: int) -> int:
    """RST (deprecated): Mark a classmethod as abstract. Returns unchanged."""
    return func


#@ requires func >= 0
#@ ensures \result == func
def abstractstaticmethod(func: int) -> int:
    """RST (deprecated): Mark a staticmethod as abstract. Returns unchanged."""
    return func


#@ requires old_cls >= 0
#@ ensures \result == old_cls
def update_abstractmethods(old_cls: int) -> int:
    """RST: 'Recalculate an abstract class's abstraction status.
    Returns cls, to allow usage as a class decorator.'
    Returns cls unchanged."""
    return old_cls

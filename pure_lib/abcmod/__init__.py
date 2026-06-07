# pure_lib/abcmod — pure-Python abc module model
# Named 'abcmod' to avoid stdlib name clash.
#
# Models abstractmethod decorator and ABC base class.
# Body-proven: abstractmethod is identity on its argument.


#@ requires func >= 0
#@ ensures \result == func
def abstractmethod(func: int) -> int:
    """Mark a method as abstract. Returns the function unchanged."""
    return func


#@ requires func >= 0
#@ ensures \result == func
def abstractclassmethod(func: int) -> int:
    """Mark a classmethod as abstract (deprecated). Returns unchanged."""
    return func


#@ requires func >= 0
#@ ensures \result == func
def abstractstaticmethod(func: int) -> int:
    """Mark a staticmethod as abstract (deprecated). Returns unchanged."""
    return func


#@ requires old_cls >= 0
#@ ensures \result == old_cls
def update_abstractmethods(old_cls: int) -> int:
    """Recalculate abstract status after class modification."""
    return old_cls

# Formal tests for pycsl_lib/abcmod — abc module model
from pycsl_lib.abcmod import abstractmethod, abstractclassmethod, abstractstaticmethod, update_abstractmethods


#@ requires func >= 0
#@ ensures \result == func
def test_abstractmethod_identity(func: int) -> int:
    """abstractmethod is a no-op decorator (returns func unchanged)."""
    return abstractmethod(func)


#@ requires func >= 0
#@ ensures \result == func
def test_abstractclassmethod_identity(func: int) -> int:
    """abstractclassmethod is a no-op decorator."""
    return abstractclassmethod(func)


#@ requires func >= 0
#@ ensures \result == func
def test_abstractstaticmethod_identity(func: int) -> int:
    """abstractstaticmethod is a no-op decorator."""
    return abstractstaticmethod(func)


#@ requires cls >= 0
#@ ensures \result == cls
def test_update_abstractmethods_identity(cls: int) -> int:
    """update_abstractmethods returns cls unchanged."""
    return update_abstractmethods(cls)

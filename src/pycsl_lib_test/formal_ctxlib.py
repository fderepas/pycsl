# Formal tests for pycsl_lib/ctxlib — contextlib module
from pycsl_lib.ctxlib import contextmanager, closing, nullcontext


#@ requires func >= 0
#@ ensures \result == func
def test_contextmanager_identity(func: int) -> int:
    """contextmanager returns the function unchanged."""
    return contextmanager(func)


#@ requires obj >= 0
#@ ensures \result == obj
def test_closing_identity(obj: int) -> int:
    """closing returns the object."""
    return closing(obj)


#@ requires val >= 0
#@ ensures \result == val
def test_nullcontext_identity(val: int) -> int:
    """nullcontext returns enter_result."""
    return nullcontext(val)

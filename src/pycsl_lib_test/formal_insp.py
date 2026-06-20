# Formal tests for pycsl_lib/insp — inspect module
from pycsl_lib.insp import (unwrap, signature, cleandoc,
                            isfunction, isclass, ismethod, ismodule,
                            getfile, getdoc, getsource, getlineno)


#@ requires func >= 0
#@ ensures \result >= 0
def test_unwrap_nonneg(func: int) -> int:
    """unwrap returns non-negative."""
    return unwrap(func)


#@ requires func >= 0
#@ ensures \result >= 0
def test_signature_nonneg(func: int) -> int:
    """signature returns non-negative."""
    return signature(func)


def test_cleandoc_str() -> str:
    """cleandoc returns a string."""
    return cleandoc("hello world")


#@ requires obj >= 0
#@ ensures \result == 0 or \result == 1
def test_isfunction_boolean(obj: int) -> int:
    """isfunction returns 0 or 1."""
    return isfunction(obj)


#@ requires obj >= 0
#@ ensures \result == 0 or \result == 1
def test_isclass_boolean(obj: int) -> int:
    """isclass returns 0 or 1."""
    return isclass(obj)


#@ requires obj >= 0
#@ ensures \result == 0 or \result == 1
def test_ismethod_boolean(obj: int) -> int:
    """ismethod returns 0 or 1."""
    return ismethod(obj)


#@ requires obj >= 0
#@ ensures \result == 0 or \result == 1
def test_ismodule_boolean(obj: int) -> int:
    """ismodule returns 0 or 1."""
    return ismodule(obj)


#@ requires obj >= 0
#@ ensures \result >= 0
def test_getdoc_nonneg(obj: int) -> int:
    """getdoc returns non-negative length."""
    return getdoc(obj)


#@ requires frame >= 0
#@ ensures \result >= 0
def test_getlineno_positive(frame: int) -> int:
    """getlineno returns positive line number."""
    return getlineno(frame)

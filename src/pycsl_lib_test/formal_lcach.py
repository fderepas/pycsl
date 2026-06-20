# Formal tests for pycsl_lib/lcach — linecache module
from pycsl_lib.lcach import getline, clearcache, getlines


#@ requires lineno >= 1
#@ ensures \result >= 0
def test_getline_nonneg(lineno: int) -> int:
    """getline returns non-negative."""
    return getline(lineno)


#@ ensures \result >= 0
def test_clearcache_nonneg() -> int:
    """clearcache returns non-negative."""
    return clearcache()


#@ requires size >= 0
#@ ensures \result >= 0
def test_getlines_nonneg(size: int) -> int:
    """getlines returns non-negative."""
    return getlines(size)

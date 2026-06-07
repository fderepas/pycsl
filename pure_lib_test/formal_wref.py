# Formal tests for pure_lib/wref — weakref
from pure_lib.wref import ref, proxy, getweakrefcount


#@ requires obj >= 0
#@ ensures \result == obj
def test_ref_identity(obj: int) -> int:
    """ref returns object id."""
    return ref(obj)


#@ requires obj >= 0
#@ ensures \result == obj
def test_proxy_identity(obj: int) -> int:
    """proxy behaves like object."""
    return proxy(obj)


#@ requires obj >= 0
#@ ensures \result >= 0
def test_weakrefcount_nonneg(obj: int) -> int:
    """Weak reference count is non-negative."""
    return getweakrefcount(obj)

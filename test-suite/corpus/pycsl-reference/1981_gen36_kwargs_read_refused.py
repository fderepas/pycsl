r"""Test 1981 — gen #36 (expected FAIL): ROUTE #232 related shape — a READ `**kwargs` parameter

`**kw` is not modelled: it was dropped from the signature, `len(kw)` read an opaque constant
shared by every call, and `f(a=3) == f(a=4, b=5)` PROVED at 3e758c0b (CPython: 1 != 2, `g()`
returns 0). A body read of a `**kwargs` parameter is now refused fail-closed.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ assigns \nothing
def f(**kw: int) -> int:
    return len(kw)


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if f(a=3) == f(a=4, b=5):
        return 1
    return 0

r"""Test 1977 — gen #36 (expected PASS): ROUTE #232 related shape — keyword actuals in a different order

`f(b=2, a=1)` binds by NAME, not by position: `a - b` is -1. CPython: `g()` returns -1.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == a - b
#@ assigns \nothing
def f(a: int, b: int) -> int:
    return a - b


#@ ensures \result == -1
#@ assigns \nothing
def g() -> int:
    return f(b=2, a=1)

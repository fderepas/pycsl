r"""Test 1978 — gen #36 (expected FAIL): ROUTE #232 related shape — reordered keywords, positional misreading

The false twin of 1977: a POSITIONAL reading of `f(b=2, a=1)` would give `2 - 1 == 1`.
CPython: `g()` returns -1.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == a - b
#@ assigns \nothing
def f(a: int, b: int) -> int:
    return a - b


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return f(b=2, a=1)

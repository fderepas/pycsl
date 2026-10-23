r"""Test 1980 — gen #36 (expected FAIL): ROUTE #232 — positional-only parameters were dropped too

`def f(a: int = 3, /)` lost `a` exactly like a keyword-only parameter; with `h(a: int = 4, /)`
both read one `val constant a`, so `f() == h()` PROVED at 3e758c0b. CPython: `g()` returns 0.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ assigns \nothing
def f(a: int = 3, /) -> int:
    return a


#@ assigns \nothing
def h(a: int = 4, /) -> int:
    return a


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if f() == h():
        return 1
    return 0

r"""Test 1979 — gen #36 (expected FAIL): ROUTE #232 — two keyword-only defaults read as ONE constant

`f(*, k=3)` and `h(*, k=4)` both read the same auto-declared `val constant k`, so `f() == h()`
PROVED at 3e758c0b. CPython: 3 != 4, `g()` returns 0.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ assigns \nothing
def f(*, k: int = 3) -> int:
    return k


#@ assigns \nothing
def h(*, k: int = 4) -> int:
    return k


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    if f() == h():
        return 1
    return 0

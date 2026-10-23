r"""Test 1356 — ROUTE #126: `f(x)` defines `h()` reading `x`; the nested def was lifted to a sibling and `x` became ONE global opaque constant, so `f(1) - f(2) == 0` PROVED while CPython returns -1. A lifted def that reads a name of its enclosing function is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ assigns \nothing
def f(x: int) -> int:
    def h() -> int:
        return x
    return h()


#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    return f(1) - f(2)

r"""Test 1986 — gen #36 (expected FAIL): ROUTE #233 — a `match` capture read as an opaque module constant

`case y:` was never bound by the `match` lowering, so both reads of `y` (one per `match`) fell
through to ONE auto-declared `val constant y : int`, and `r - s = y - y = 0` PROVED at 87ff222f.
CPython: `f(0)` returns `0 - 1 = -1`, so `\result == 0` is false.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    r = 0
    s = 0
    match x:
        case y:
            r = y
    match x + 1:
        case y:
            s = y
    return r - s

r"""Test 1989 — gen #36 (expected FAIL): ROUTE #233 — a capture read AFTER its `match`

A capture binding outlives the `match` (Python function scope). Both post-`match` reads of
`y` were the same opaque constant, so `a - y == 0` PROVED at 87ff222f; CPython returns -1.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    match x:
        case y:
            pass
    a = y
    match x + 1:
        case y:
            pass
    return a - y

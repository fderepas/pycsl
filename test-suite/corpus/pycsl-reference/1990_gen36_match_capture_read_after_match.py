r"""Test 1990 — gen #36 (expected PASS): ROUTE #233 — a capture is a real local after its `match`

`y` keeps the subject's value after the `match`, as in CPython (`f(x) == x`).
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == x
#@ assigns \nothing
def f(x: int) -> int:
    match x:
        case y:
            pass
    return y

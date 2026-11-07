r"""Test 1987 — gen #36 (expected PASS): ROUTE #233 — a bare capture binds the subject

`case y:` binds `y` to the subject as a real local (`y = x` at the head of the arm), so the
arm's read of `y` IS `x`. Refused-as-unprovable at 87ff222f (the read was an opaque constant).
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == x + 1
#@ assigns \nothing
def f(x: int) -> int:
    r = 0
    match x + 1:
        case y:
            r = y
    return r

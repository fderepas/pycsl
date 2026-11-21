r"""Test 1988 — gen #36 (expected PASS): ROUTE #233 — `case 1 | 2 as y:` binds the subject

The `as` capture binds the whole subject when its inner or-pattern matches; with `x == 2` the
first arm is taken and `r = y = 2`. Unprovable at 87ff222f (opaque constant `y`).
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ requires x == 2
#@ ensures \result == 2
#@ assigns \nothing
def f(x: int) -> int:
    r = 0
    match x:
        case 1 | 2 as y:
            r = y
        case _:
            r = 0
    return r

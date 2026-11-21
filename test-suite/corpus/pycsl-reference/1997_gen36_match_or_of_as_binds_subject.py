r"""Test 1997 — gen #36 (expected PASS): ROUTE #233 — `case (1 as y) | (2 as y):` binds the subject

Each alternative's `as` captures the whole subject; with `x == 2` the arm binds `y = 2`.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ requires x == 2
#@ ensures \result == 2
#@ assigns \nothing
def f(x: int) -> int:
    r = 0
    match x:
        case (1 as y) | (2 as y):
            r = y
        case _:
            r = 0
    return r

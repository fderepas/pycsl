r"""Test 1991 — gen #36 (expected FAIL, refused): ROUTE #233 — a GUARDED capture arm

Python binds `y` BEFORE the guard and keeps it when the guard fails, so the `case _:` arm
returns 5 here. At 87ff222f the guard read the local `y = 0` and `\result == 0` PROVED. The
capture-then-guard order is not modelled: refused fail-closed (route #233 diagnostic).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires x == 5
#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    y = 0
    match x:
        case y if y > 10:
            return 1
        case _:
            return y

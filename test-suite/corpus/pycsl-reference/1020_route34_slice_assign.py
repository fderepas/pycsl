"""Test 1020 — ROUTE #34: a SLICE assignment.

FALSE OF THE PROGRAM: `a[0:1] = [9]` replaces the first element, so Python
returns 9. Proved `\result == 5` at c4233fed.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    a = [5, 6]
    a[0:1] = [9]
    return a[0]

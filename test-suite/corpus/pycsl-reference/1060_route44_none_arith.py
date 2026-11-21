"""Test 1060 — ROUTE #44 negative witness (c): ARITHMETIC on `None` proved a VALUE.

FALSE OF THE PROGRAM: `None + 5` raises `TypeError` in Python; the function has no
value at all.

The guard is not the only consumer, and this witness is here for the same reason 1044
is in route #41: an equality-only fix would have been the same mistake one operator
later. At the parent commit d0493cea `\\result == 5` PROVED.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    x = None
    return x + 5

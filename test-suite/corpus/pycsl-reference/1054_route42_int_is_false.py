"""Test 1054 — ROUTE #42 negative witness (b): `<int> is False` was DECIDABLY TRUE.

FALSE OF THE PROGRAM: Python's `0 is False` is False, so `f()` returns 0.

The `False` half of 1053. `False` int-encodes to `0`, so the guard read `!x = 0`,
which is decidably TRUE for `x = 0`. At the parent commit 0f3906bd `\\result == 7`
PROVED. Both halves matter: a fix that closed only `is True` would have been the
same mistake one operand later, exactly as witness 1044 records for route #41.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 0
    if x is False:
        return 7
    return 0

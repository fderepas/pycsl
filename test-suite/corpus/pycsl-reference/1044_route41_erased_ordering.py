"""Test 1044 — ROUTE #41 negative witness (d): an erased local ORDERED against 1.

FALSE OF THE PROGRAM: `<generator> < 1` raises `TypeError` in Python; there is no run
in which this function returns 7.

The ordering consumer is what makes the point that an equality-only patch would have
been the same mistake one step later: the erasure is decidable under EVERY int
operator, not just `==`. At the parent commit c37f0059 `\result == 7` PROVED.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = (i for i in [1, 2, 3])
    if x < 1:
        return 7
    return 0

"""Test 1037 — ROUTE #40 negative witness (b): `... == 0` was DECIDABLY TRUE.

FALSE OF THE PROGRAM: `Ellipsis == 0` is False in Python, so Python returns 0.

This is the half that shows the defect is a CONFLATION, not a loss. A lost value is
opaque and decides nothing; `...` was lowered to the *literal* 0, so `x == 0` proved
outright. At the parent commit b5fb0688 `\result == 7` PROVED.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = ...
    if x == 0:
        return 7
    return 0

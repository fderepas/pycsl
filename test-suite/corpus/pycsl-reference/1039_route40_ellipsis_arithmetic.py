"""Test 1039 — ROUTE #40 negative witness (d): arithmetic on `...`.

FALSE OF THE PROGRAM: `Ellipsis + 5` raises `TypeError` in Python; there is no run in
which this function returns 5.

At the parent commit b5fb0688 the emission was `x := 0; !x + 5` and `\result == 5`
PROVED.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    x = ...
    return x + 5

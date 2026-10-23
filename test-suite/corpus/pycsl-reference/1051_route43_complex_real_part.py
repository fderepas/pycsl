"""Test 1051 — ROUTE #43 negative witness (b): the REAL part decided the comparison.

FALSE OF THE PROGRAM: `(1+2j) == 1` is False in Python, so this returns 0.

`1 + 2j` lowered to the integer `1`, so `x == 1` was decidably TRUE. At the parent commit
f2873419 `\result == 7` PROVED. This is the half that shows the defect is a CONFLATION,
not a loss: a lost value decides nothing.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 1 + 2j
    if x == 1:
        return 7
    return 0

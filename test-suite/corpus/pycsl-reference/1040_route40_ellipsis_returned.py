"""Test 1040 — ROUTE #40 negative witness (e): `return ...`.

FALSE OF THE PROGRAM: Python returns the `Ellipsis` singleton, not the integer 0.

At the parent commit b5fb0688 the emission was `raise (Return 0)` and `\result == 0`
PROVED. The value is now opaque, so no integer claim about it is provable.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    return ...

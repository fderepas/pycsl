"""Test 1066 — ROUTE #45 negative witness (b): NaN survives ARITHMETIC, and so must the fix.

FALSE OF THE PROGRAM: `float("nan") + 1` is NaN, and `nan == nan` is False, so `f()`
returns 0.

IEEE 754 makes every arithmetic operation with a NaN operand NaN. A fix that recognized
only the direct `float("nan")` local would have been the same mistake one operator later —
the lesson witness 1044 records for route #41 and 1054 for route #42 — so route #45's
recognizer PROPAGATES through `+ - * / // % **` and unary `+ -`, and this driver is what
holds it to that. Comparisons do NOT propagate: they yield a bool, not a NaN.

At the parent commit 3bbfb59f `\\result == 7` PROVED.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = float("nan")
    y = x + 1
    if y == y:
        return 7
    return 0

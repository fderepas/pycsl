"""Test 1059 — ROUTE #44 negative witness (b): `<int> is None` WAS DECIDABLY TRUE.

FALSE OF THE PROGRAM: `0 is None` is False in Python, so `f()` returns 0.

The mirror direction of 1058: here the integer is the bound name and `None` is the
literal. Twelve recognizers above the fall-through model a `None` test faithfully, each
for a shape whose optionality the model carries; UNDERNEATH them the comparison simply
fell through with the `None` node lowered to `0`, so the guard read `!x = 0`. At the
parent commit d0493cea `\\result == 7` PROVED.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 0
    if x is None:
        return 7
    return 0

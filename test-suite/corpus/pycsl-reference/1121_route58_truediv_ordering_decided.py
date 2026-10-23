"""Test 1121 — ROUTE #58 negative witness (a): int/int TRUE DIVISION was an EXACT REAL
division, so it decided an ordering Python answers the other way.

FALSE OF THE PROGRAM: `1 / 3` and the literal `0.3333333333333333` are the SAME
binary64 value — the literal is precisely the shortest decimal that round-trips to
it — so `(1/3) > 0.3333333333333333` is `False` in Python. Over the EXACT reals one
third is `0.333…` repeating and IS greater than that terminating 16-digit decimal,
so the goal closed.

WHY ROUTE #53'S REPAIR DID NOT COVER THIS. #53 made float-operand arithmetic go
through one uninterpreted deterministic symbol, but that path is guarded on BOTH
operands being float. `1 / 3` has two INT operands and took an entirely different
branch with its own bridge, `val float_truediv_op (a b: int) : real ensures
{ result = (from_int a /. from_int b) }` — the same defect one costume over, and
invisible from the first because the two code paths never meet.

THE GENERAL LESSON, and it is the one routes #50/#51 already paid for at `str`:
**a repair covers the PATH it edits, not the SEMANTICS it means to fix.** After
closing a route, probe the other paths that reach the same semantics before
recording it closed. This route was found by doing exactly that to #53.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result > 0.3333333333333333
#@ assigns \nothing
def f() -> float:
    return 1 / 3

"""Test 1111 — ROUTE #56 negative witness (b): ARITHMETIC on a `None` Optional-union
local, which is the stronger shape — the model does not merely COMPARE `None` to zero,
it COMPUTES with it.

FALSE OF THE PROGRAM: Python raises
`TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'`. It does not
return 1; it does not return at all.

At the parent commit this PROVED `\\result == 1`, because the value-read projection
answered the `None` arm with the carrier's zero and `0 + 1 = 1`. So a program that
CRASHES was given a total, decided, wrong answer.

This matters beyond 1108 because it shows the sentinel is not confined to an equality
test that a reader might dismiss as a corner: any operation that consumes the value
consumes a zero. The repair — answering route #44's existing `pycsl_none` opaque in the
non-Some arm — closes this shape by the same stroke, because `pycsl_none + 1 = 1` is
undecided.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Optional


#@ requires c <= 0
#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    x: Optional[int] = None
    if c > 0:
        x = 5
    return x + 1

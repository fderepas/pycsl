"""Test 1109 — ROUTE #56 POSITIVE control (a): the `is None` GUARD stays faithful.

TRUE OF THE PROGRAM: with `c <= 0`, `x` is `None`, the guard is taken, and `f`
returns 9.

Route #56's repair changes the non-Some arm of the VALUE-READ projection only.
The `is None` test does not go through that projection at all — it derefs the RAW
`!x` and matches on the constructor — so this must keep proving. It pins the half
of the behaviour the repair must NOT cost: a fail-closed repair that also broke
the guard would have made `Optional` locals useless rather than sound.
"""
_ = 0  # anchor
from typing import Optional


#@ requires c <= 0
#@ ensures \result == 9
#@ assigns \nothing
def f(c: int) -> int:
    x: Optional[int] = None
    if c > 0:
        x = 5
    if x is None:
        return 9
    return 0

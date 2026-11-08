"""Test 1213 — ROUTE #79, THE HONEST COST: the TRUE claim is unprovable too, and that is
the correct outcome rather than a regression.

`self.n = len(items)` is not recoverable at the allocation site: `__init__` is inlined as a
record literal, and `len(items)` is not substitutable into one. So the repair gives the
field an UNCONSTRAINED value, and BOTH `\\result == 0` (false, 1212) and `\\result == 3`
(true, this file) stop proving.

**THIS IS THE DELIBERATE CHOICE, AND ITS BOUND IS 1215.** Contrast route #82, whose value
WAS recoverable — a keyword-only parameter the capture rule simply failed to read — and
which was therefore closed by a FAITHFUL CAPTURE that made every true twin PROVE, a
completeness GAIN. The rule the campaign now applies: PREFER A FAITHFUL CAPTURE WHEREVER THE
INFORMATION EXISTS, AND FALL BACK TO UNCONSTRAINED ONLY WHERE IT GENUINELY DOES NOT.

Recording the cost as a NEGATIVE WITNESS rather than leaving it untracked is the point: if a
later change makes this claim provable again, that is either a real completeness gain or
route #79 reopening, and the suite will say so either way. An untracked failure is invisible
to that ratchet.
"""
# pycsl-expected: FAIL
from typing import List


class C:
    n: int

    #@ assigns self.n
    def __init__(self, items: List[int]) -> None:
        self.n = len(items)


#@ requires True
#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    c = C([1, 2, 3])
    return c.n

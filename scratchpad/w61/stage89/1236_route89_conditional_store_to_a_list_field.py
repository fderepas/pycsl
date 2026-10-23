"""Test 1236 — ROUTE #89: a CONDITIONAL store to a LIST field, in the branch that does not run.

Route #83 made a field stored inside control flow unconstrained, but its override in
`module6_whyml/expressions.py` is gated on `field_types.get(fn) not in _NONSCALAR` — **it
fences SCALARS ONLY**. That was correct when it was written, because the collection arms then
carried no DECIDABLE contents to be wrong about. Routes #85 and #87 re-armed it by making a
dict/list field literal FAITHFUL, and `_collect_class_fields` collects those literals with an
`ast.walk`, so the store nested in the `if` is SEEN and — being later in the walk — WINS.

Measured before the repair: this claim PROVED, CPython returns 1, and the TRUE twin was
REFUSED. Constructed with `C(0)` so the guard is FALSE and the real list is `[1, 2]`.

**A COMPLETENESS GAIN CAN RE-ARM A SOUNDNESS DEFECT AN EARLIER REPAIR HAD FENCED OFF, WITHOUT
TOUCHING EITHER OF THEM.** #83's fence and #85/#87's captures are each correct in isolation:
the fence was scoped by TYPE, and the captures widened what a TYPE can decide.

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL
from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self, k: int) -> None:
        self.xs = [1, 2]
        if k > 0:
            self.xs = [7, 8]


#@ requires True
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = C(0)
    return c.xs[0]

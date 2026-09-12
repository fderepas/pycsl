"""Test 1225 — ROUTE #87's NEGATIVE TEST OF ITS OWN OPTIMIZATION.

The repair records a list field's literal in the IR **only when doing so changes the answer**.
An ALL-ZERO literal already lowered faithfully to the `(Array.make n 0)` the emitter always
produced, so recording it would add an IR key that moves a FROZEN CONFORMANCE GOLDEN (0595's
`self.disk: list = [0]*8`) while changing no emitted byte.

**THAT GOLDEN DID MOVE, AND THE FIX WAS NOT TO RE-BLESS IT.** Rule (k) forbids refreshing a
frozen golden to make a gate green. The right answer was to stop emitting information that
carries none — the conformance gate was RIGHT that the IR had changed for a file whose
behaviour had not, and it was pointing at a real over-reach in the repair, not at a stale
golden. Conformance returned to 38/38 core + 38/38 front-end with no golden touched.

**THIS FILE IS THE NEGATIVE TEST FOR THAT NARROWING** (rule (l): negative-test every new gate
by removing the thing it should catch). The condition is "all elements are ZERO", NOT "all
elements are EQUAL" — so an all-equal NON-ZERO literal like `[7, 7, 7]` must STILL be captured,
because the old emitter gave it `Array.make 3 0` and `c.xs[0] == 0` is FALSE of the program
(CPython returns 7). Without this file, narrowing the condition from "not all zero" to "not all
equal" would close route #87 for `[1,2,3]`, leave it WIDE OPEN for `[7,7,7]`, and pass every
other test in the suite.

This file is `pycsl-expected: FAIL`: the claim is FALSE of the program and must not prove.
"""
# pycsl-expected: FAIL
from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [7, 7, 7]


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.xs[0]

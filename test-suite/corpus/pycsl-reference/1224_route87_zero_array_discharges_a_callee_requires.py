"""Test 1224 — ROUTE #87's CROSS-CALL carrier: the zero-filled array DISCHARGED a callee's
`#@ requires` that the running program VIOLATES.

`g` demands `xs[0] == 0`. The program passes `c.xs == [1, 2, 3]`, so CPython violates the
precondition outright — yet the obligation was discharged against the zero-filled array, and
the file printed *All contracts formally proven*.

**PROBE THE REQUIRES-DISCHARGE DIRECTION FOR EVERY VALUE-ERASURE ROUTE.** A wrong VALUE gives a
false postcondition in whatever reads it; a wrongly-DISCHARGED precondition breaks the
caller/callee contract itself, so every downstream proof leaning on `g`'s precondition is
unsound too. Routes #80, #82, #83, #85, #86 and now #87 ALL turned out to have this escalation,
without exception — it is one extra driver and it has never once failed to apply.

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires xs[0] == 0
#@ ensures \result == 0
#@ assigns \nothing
def g(xs: List[int]) -> int:
    return 0


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2, 3]


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return g(c.xs)

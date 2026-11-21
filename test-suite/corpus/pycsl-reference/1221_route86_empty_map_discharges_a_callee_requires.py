"""Test 1221 — ROUTE #86's SERIOUS CARRIER: the substituted empty map DISCHARGED a callee's
`#@ requires` that the running program VIOLATES.

`g` demands `1 not in d`. The program passes `c.d == {1: 5}`, so CPython violates the
precondition outright — yet the caller's obligation was discharged against the empty map the
coercion substituted, and the whole file printed *All contracts formally proven*.

**WHY THIS CARRIER IS KEPT SEPARATE FROM THE VALUE CARRIER (1220).** A wrong VALUE produces a
false postcondition in the function that reads it; a wrongly-DISCHARGED precondition breaks the
caller/callee contract itself, so the defect crosses the call graph and every downstream proof
that leaned on `g`'s precondition is unsound too. Routes #80, #82 and #83 each turned out to
have this same escalation, and in every case it was the carrier that showed the defect was not
confined to one expression. **PROBE THE REQUIRES-DISCHARGE DIRECTION FOR EVERY VALUE-ERASURE
ROUTE** — it is one extra driver and it is what distinguishes a local wrong answer from a
cross-procedural one.

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL
from typing import Dict


#@ requires 1 not in d
#@ ensures \result == 0
#@ assigns \nothing
def g(d: Dict[int, int]) -> int:
    return 0


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C()
    return g(c.d)

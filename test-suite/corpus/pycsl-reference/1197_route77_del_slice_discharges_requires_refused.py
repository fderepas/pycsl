"""Test 1197 — ROUTE #77 ESCALATES PAST THE POSTCONDITION: the stale value DISCHARGES A
CALLEE'S `requires` AT A CALL SITE.

This is the carrier that lifts route #77 above "a postcondition nobody would write" (see
1194 for the full route). The value read after the erased slice delete is handed to another
function's PRECONDITION, and the emitter discharges it. Measured, before the refusal:

    #@ requires x == 1
    def g(x: int) -> int: return x

    xs: List[int] = [1, 2, 3]
    del xs[0:2]
    return g(xs[0])          # CPython calls g(3) — the precondition is FALSE at runtime

    [+] Verification SUCCESS! All contracts formally proven.

So the defect propagated across the CALL GRAPH rather than staying local to the clause that
mentioned the stale value — the same escalation shape route #76 had.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires x == 1
#@ ensures \result == x
#@ assigns \nothing
def g(x: int) -> int:
    return x


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2, 3]
    del xs[0:2]
    return g(xs[0])

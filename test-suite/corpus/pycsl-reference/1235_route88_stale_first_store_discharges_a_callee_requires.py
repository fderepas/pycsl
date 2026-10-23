"""Test 1235 — ROUTE #88's ESCALATION: the stale value CROSSES THE CALL GRAPH.

The first store's value `1` is not merely returned — it DISCHARGES a callee's `requires m == 1`
at a call site where the runtime value is `2`. So the defect is not confined to a
postcondition about the constructing function; it silently establishes a precondition the
program never establishes, and everything the callee proves from it is unsound.

Measured before the repair: PROVED. This is the same escalation shape recorded for routes #79,
#83 and #87, and it is the reason a field-default defect is severity 1 rather than a precision
complaint.

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL


class C:
    n: int

    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 1
        self.n = 2


#@ requires m == 1
#@ ensures \result == m
#@ assigns \nothing
def g(m: int) -> int:
    return m


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    return g(c.n)

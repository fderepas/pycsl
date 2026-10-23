"""Test 1203 — ROUTE #80, third carrier: the stale attribute DISCHARGES A CALLEE'S
`requires`, so the defect CROSSES THE CALL GRAPH.

This is the escalation that lifts #80 out of "a wrong clause in one function". The erased
`del c.x` leaves the model holding 10, and that stale value is then passed to a callee
whose precondition demands exactly 10:

    #@ requires v == 10
    def g(v: int) -> int: return v

    c = C(); del c.x; return g(c.x)

PyCSL DISCHARGED `g`'s `requires` — but at runtime `c.x` has fallen back to the class
attribute 5, so the call site violates the callee's contract while the run still reports
"All contracts formally proven". The TRUE twin (`requires v == 5`, `ensures \\result == 5`)
is REFUSED, so this is a route in both directions like the other two carriers.

A precondition discharged from a stale value is worse than a wrong postcondition: the
callee's own proof is sound relative to a `requires` that the caller never actually
establishes, so the unsoundness is laundered through a correct proof.

Refused at the same site as 1201/1202. This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL


class C:
    x: int = 5

    #@ assigns self.x
    def __init__(self) -> None:
        self.x = 10


#@ requires v == 10
#@ ensures \result == v
#@ assigns \nothing
def g(v: int) -> int:
    return v


#@ requires True
#@ ensures \result == 10
#@ assigns \nothing
def f() -> int:
    c = C()
    del c.x
    return g(c.x)

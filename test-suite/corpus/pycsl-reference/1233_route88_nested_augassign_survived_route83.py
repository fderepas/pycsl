"""Test 1233 — ROUTE #88: a NESTED augmented store SURVIVED ROUTE #83's REPAIR.

Route #83 made a field stored inside control flow unconstrained, but its `_init_unknown` walk
tests `ast.Assign` and `ast.AnnAssign` only. An augmented store nested in an `if` therefore
matched NEITHER route's guard: #83 did not see it because it is not an `Assign`, and #88's
top-level pass does not see it because it is nested. Measured after #83 landed and before #88:
this claim PROVED, CPython returns 5.

**A CARRIER THAT SURVIVES A LANDED REPAIR IS A SECOND ROUTE, NOT A FAILED REPAIR** — gen #10's
generator 2, which is what produced route #86. Two guards that each cover part of a shape are
indistinguishable from one guard that covers all of it until a carrier falls in the gap between
them.

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL


class C:
    n: int

    #@ assigns self.n
    def __init__(self, k: int) -> None:
        self.n = 0
        if k > 0:
            self.n += 5


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C(7)
    return c.n

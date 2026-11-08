"""Test 1238 — ROUTE #89's OVER-BREADTH BOUND for the LIST arm: route #87's capability survives.

The #89 repair makes a collection field UNCONSTRAINED when — and only when — the constructor
also stores it inside control flow. A repair that simply stopped trusting list-field literals
would satisfy 1236 and 1237 while UNDOING ROUTE #87's completeness gain, and every
expected-FAIL witness in the family would still pass. Only a file that must STILL PROVE can
detect that, which is why this one exists and why it is the same instrument as 1223, 1225,
1229 and 1234.

**NEGATIVE-TEST THE NARROWING, NOT JUST THE REPAIR.**
"""
from typing import List


class C:
    xs: List[int]

    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2, 3]


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.xs[0]

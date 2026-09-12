"""Test 1239 — ROUTE #89's OVER-BREADTH BOUND for the DICT arm: route #85's capability survives.

The dict half of 1238. A `self.d = {1: 5}` with no conditional store must still prove
`c.d[1] == 5` after the #89 repair — that is route #85's faithful `map_update_some` chain, and
losing it would be a completeness regression hidden behind a green soundness gate.
"""
from typing import Dict


class C:
    d: Dict[int, int]

    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}


#@ requires True
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.d[1]

"""Test 1217 — ROUTE #85, THE SHARPER CARRIER: the model was wrong about the CONTENTS of the
map, not merely about a present-guard.

`c.d.get(1, 0)` proved `\\result == 0` where CPython returns 5. The distinction matters
because several closed routes in this family (#55, #60) are about a GUARD being decided or a
LENGTH being wrong; this one reads a VALUE out of a map the model believes is empty and gets
the missing-key default. Route #48's closing note makes the same point about a seeded
`Counter`: an empty collection does not merely lose the seed, it makes the missing-key default
DECIDABLE, and the emitter then proves definite facts from it.

This file is `pycsl-expected: FAIL`.
"""
# pycsl-expected: FAIL
from typing import Dict


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
    return c.d.get(1, 0)

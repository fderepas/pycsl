"""Test 0519 — record-typed parameters (no-more-int-2 Track 3).

A bare class-typed parameter is reconstructed as its Why3 record (was coarsened to `int` with an
opaque `getattr_<cls>`), so `p.x` is a direct field read in BOTH the body and the contract — a
property of a record param's fields discharges. Read-only: mutating a record param is out of scope
(Why3 records are by-value; see the plan)."""
_ = 0  # anchor
class Point:
    def __init__(self, a: int, b: int):
        self.x = a
        self.y = b


#@ requires p.x == 3
#@ requires p.y == 4
#@ ensures \result == 7
def add_coords(p: Point) -> int:
    return p.x + p.y

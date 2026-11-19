"""WL-04e false-twin — a FALSE cross-element conflation must stay UNPROVEN.

Guards the WL-04e fix from vacuity: over a flat `List[Point]` (plain positional-
`__init__` class, realized as `array point`) `f` returns `a[0].x` but claims
`\result == a[1].x`. Distinct array slots hold INDEPENDENT records, so a cross-element
field conflation is NOT provable — PROVEN here would mean the element model collapsed
every element into one opaque value (the pre-fix `array int` failure mode). Verdict:
UNPROVEN."""
_ = 0
from typing import List


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


#@ requires len(a) > 1
#@ ensures \result == a[1].x
def f(a: List[Point]) -> int:
    return a[0].x

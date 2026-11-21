"""WL-04b false-twin — a FALSE cross-field conflation must stay UNPROVEN.

Guards the WL-04b fix from vacuity: `f` returns `a[i].x` but claims `\result ==
a[i].y`. For a `List[Point]` the record's `x`/`y` are DISTINCT independent labels, so
this is NOT provable (PROVEN here would mean the element model conflated the fields).
Verdict: UNPROVEN."""
_ = 0
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i].y
def f(a: List[Point], i: int) -> int:
    return a[i].x

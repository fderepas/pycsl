"""WL-07 (WL-04c lift) — a `@dataclass` LITERAL element is now faithful — POSITIVE.

WL-04c had to FAIL-CLOSE a `List[<dataclass>]` literal because the `@dataclass`
constructor dropped its args (so `[Point(1, 2)][0].x` could not be projected to the
faithful `1`). With WL-07 the dataclass ctor is faithful — its `init_params`/
`init_body` are synthesized, so the WL-04c faithful-record gate now ADMITS the
dataclass, its literal builds `array <record>` with the args threaded, and
`[Point(1, 2)][0].x == 1` PROVES. Verdict: PROVEN (was TYPEERR / fail-closed)."""
_ = 0
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ ensures \result == 1
def literal_elem_x() -> int:
    a = [Point(1, 2), Point(3, 4)]
    return a[0].x


#@ ensures \result == 4
def literal_elem_y() -> int:
    a = [Point(1, 2), Point(3, 4)]
    return a[1].y


#@ ensures \result[0].x == 1
#@ ensures \result[1].y == 4
def make_points() -> List[Point]:
    return [Point(1, 2), Point(3, 4)]

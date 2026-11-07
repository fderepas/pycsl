"""WL-05d (T8) — BOUNDARY: a field store on a record PARAM whose class is ALSO used as a
`List[<record>]` element elsewhere is REJECTED (verdict REJECTED).

`Point` is pinned PURE globally because `total` takes a `List[Point]`. A standalone param
`p: Point` of that (now-immutable) class therefore cannot carry a caller-visible `p.x <- v`
store (Why3 would type-reject the `<-`). PyCSL rejects it cleanly at module6-whyml rather
than emit ill-typed WhyML."""
_ = 0
from typing import List
from dataclasses import dataclass
@dataclass
class Point:
    x: int
    y: int
#@ ensures \result >= 0
def total(a: List[Point]) -> int:
    return len(a)
#@ ensures p.x == 5
def setx(p: Point) -> None:
    p.x = 5

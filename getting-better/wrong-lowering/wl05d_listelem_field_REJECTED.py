"""WL-05d (T8) — BOUNDARY: a `List[<record>]` ELEMENT field store `a[i].x = v` is
REJECTED (verdict REJECTED; was an UNSOUND silent no-op).

`List[Point]` lowers to `array point` with a PURE (immutable) `point` element (Why3
forbids a mutable element inside `array`). There is NO sound `<-` store for `a[i].x`, so
`a[0].x = 5` fails CLOSED with a clear diagnostic. Before WL-05d it was a silent no-op
fail-OPEN: `requires a[0].x == 3` then `ensures a[0].x == 3` proved Valid after a real
mutation to 5. Rebuild the element (`a[i] = Point(...)`) instead."""
_ = 0
from typing import List
from dataclasses import dataclass
@dataclass
class Point:
    x: int
    y: int
#@ requires len(a) > 0
#@ ensures a[0].x == 5
def setx(a: List[Point]) -> None:
    a[0].x = 5

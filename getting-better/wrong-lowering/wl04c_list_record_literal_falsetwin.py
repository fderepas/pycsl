"""WL-04c false-twin — a FALSE cross-field conflation must stay UNPROVEN.

Guards the WL-04c fix from vacuity: `f` builds `a = [Point(1, 5)]` and returns
`a[0].x` (== 1) but claims `\result == 5`. For the faithful `array <record>`
literal model, the record's `x` and `y` are DISTINCT independent labels, so the
5 (which is `a[0].y`) is NOT the returned `a[0].x` — this is NOT provable (PROVEN
here would mean the literal element model conflated the two fields). Verdict:
UNPROVEN."""
_ = 0
from typing import NamedTuple, List


class Point(NamedTuple):
    x: int
    y: int


#@ ensures \result == 5
def f() -> int:
    a = [Point(1, 5)]
    return a[0].x

"""Test 0861 — WL-05d regression lock (NEGATIVE): `List[<record>]` element field store is REJECTED. # pycsl-expected: FAIL

wrong-lowering-to-fix.md §WL-05d (fail-closed boundary). `List[Point]` lowers to
`array point` with a PURE (immutable) `point` element — Why3 forbids a mutable element
inside `array`. There is NO sound `<-` store for `a[i].x`, so `a[0].x = 5` must fail
CLOSED (clean PYCSL-WHYML-PARAM-COLLECTION-MUT rejection). Before WL-05d it was a silent
no-op fail-OPEN (a caller could prove `a[0].x` unchanged after a real mutation). A clean
rejection is a SOUND refusal to lower ⇒ XFAIL. Rebuild the element (`a[i] = Point(...)`).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
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

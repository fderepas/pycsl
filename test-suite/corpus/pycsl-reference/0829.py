"""Test 0829 — WL-04b regression lock (POSITIVE, List[<dataclass>]): a FLAT
`List[Point]` PARAMETER now realizes its element as the faithful RECORD type
(`array point`), so an element field read `a[i].x` is a native record projection —
not the opaque `get_x(a[i])` collapse over an int element.

Before the fix, a `List[Point]`-annotated PARAMETER lowered to `array int` with the
element read `a[i].x` collapsed to a deterministic-but-opaque `get_x(a[i])`, so a
concrete field property `\result == a[i].x` could only be re-expressed through that
getter (sound but content-opaque). PyCSL now realizes a flat `List[Point]` param as
`array point` (the record-leaf analog of the WL-04 str/float `array string`/`array
real` flat model; Why3 forbids a mutable element inside `array`, so the element
record `point` is emitted PURE), so `a[i]` reads a real `point` and `a[i].x`
projects the faithful `x` field — the true field property PROVES.

Ground truth: for a list `a` of Points, `a[i].x` / `a[i].y` are the i-th element's
independent fields. Twin: 0831 (# pycsl-expected: FAIL) asserts a FALSE cross-field
claim (returns `a[i].x` but claims `== a[i].y`), which must NOT be provable.
"""
_ = 0  # anchor
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i].x
def get_x(a: List[Point], i: int) -> int:
    """A flat `List[Point]` element's field is a NATIVE record projection."""
    return a[i].x


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i].y
def get_y(a: List[Point], i: int) -> int:
    """The sibling field `y` is independent of `x` (distinct record labels)."""
    return a[i].y


if __name__ == "__main__":
    pts = [Point(1, 2), Point(3, 4), Point(5, 6)]
    assert get_x(pts, 2) == 5
    assert get_y(pts, 0) == 2

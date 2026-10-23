"""Test 0843 — WL-04e regression lock (POSITIVE, `List[<plain-class>]` PARAM/RETURN
element): a flat `List[Point]` where `Point` is a PLAIN class with an explicit
positional `__init__` (`def __init__(self, x, y): self.x = x; self.y = y`) — NOT a
`@dataclass`/`NamedTuple`/recognized `Tuple` — is now realized as the faithful RECORD
type (`array point`, record emitted PURE), so an element field read `a[i].x` is a
native record projection, not the opaque `get_x` over a collapsed `array int`.

Before the fix a plain positional-`__init__` class was not recognized as a list-element
record, so `List[Point]` collapsed to `array int` and `a[i].x` read the opaque
`get_x(a[i])`; a construct-store-read-back field property was UNPROVABLE. PyCSL now
recognizes such a content-faithful data record (`_m5_is_plain_positional_record_class`,
the plain-class analog of the WL-04b `@dataclass`/`NamedTuple` element): `a[i]` reads a
real `point`, `a[i].x` projects the faithful field, and a constructed record stored into
the array (`a[0] = Point(5, 6)`, the faithful `{ x = 5; y = 6 }`) reads its written
field back.

Ground truth: `read_field(a, i) == a[i].x`; after `a[0] = Point(5, 6)`, `a[0].x == 5`.
Twin: 0844 (# pycsl-expected: FAIL) asserts a FALSE cross-element conflation, which must
NOT be provable.
"""
_ = 0  # anchor
from typing import List


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


#@ requires 0 <= i
#@ requires i < len(a)
#@ ensures \result == a[i].x
def read_field(a: List[Point], i: int) -> int:
    """A flat `List[Point]` (plain-ctor class) PARAMETER element field is a native
    record projection `(a[i]).x`."""
    return a[i].x


#@ requires len(a) > 0
#@ ensures \result == 5
def store_read(a: List[Point]) -> int:
    """A faithful record STORED into the array element reads its written field back."""
    a[0] = Point(5, 6)
    return a[0].x


if __name__ == "__main__":
    pts = [Point(3, 4), Point(7, 8)]
    assert read_field(pts, 0) == 3
    assert read_field(pts, 1) == 7
    pts2 = [Point(0, 0)]
    assert store_read(pts2) == 5

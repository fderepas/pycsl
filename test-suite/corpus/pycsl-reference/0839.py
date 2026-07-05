"""Test 0839 — WL-04c regression lock (POSITIVE, `List[<record>]` LITERAL): a list
LITERAL of full-arity record constructors now realizes its elements as the faithful
RECORD type (`array <record>`) with the constructor args threaded into the fields,
so an element field read `a[i].field` (on the local) or `\result[i].field` (on a
`-> List[R]` return) is a native record projection — not the opaque `get_field` /
int-coercion collapse.

Before the fix, a list literal `[Point(1, 2), Point(3, 4)]` ran every element
through `_coerce_to_int`, so a record-constructor element collapsed to an opaque int
and `a[i].field` was content-opaque / ill-typed at a record use site (TYPEERR).
PyCSL now threads the record CONSTRUCTOR into the list-literal seam (the construction
analog of the WL-04b flat `List[<record>]` PARAMETER element): each element becomes
the faithful record literal `{ x = 1; y = 2 }`, the local is registered as a
record-array local (and a `-> List[Point]` return resolves to `array point`), so
`a[i].x` / `\result[i].y` project the real fields. The element record is emitted PURE
(Why3 forbids a mutable element inside `array`).

Faithfulness is REQUIRED: only a record whose constructor sets every field from a
positional param (here a `NamedTuple`) is threaded; a `@dataclass` whose ctor drops
its args stays fail-closed (documented residual). Ground truth: for
`a = [Point(1, 2), Point(3, 4)]`, `a[0].x == 1` and `a[1].y == 4`, and the two
elements' fields are independent. Twin: 0840 (# pycsl-expected: FAIL) asserts a FALSE
cross-field conflation, which must NOT be provable.
"""
_ = 0  # anchor
from typing import NamedTuple, List


class Point(NamedTuple):
    x: int
    y: int


#@ ensures \result == 1
def first_x() -> int:
    """A record-list LITERAL local's element field is a native record projection."""
    a = [Point(1, 2), Point(3, 4)]
    return a[0].x


#@ ensures \result == 4
def second_y() -> int:
    """The sibling field `y` of a later element is independent of `x`."""
    a = [Point(1, 2), Point(3, 4)]
    return a[1].y


#@ ensures \result[0].x == 1
#@ ensures \result[1].y == 4
def make_points() -> List[Point]:
    """A `-> List[Point]` return built by a literal — `\result[i].field` reads the
    faithful field of the i-th element."""
    return [Point(1, 2), Point(3, 4)]


if __name__ == "__main__":
    assert first_x() == 1
    assert second_y() == 4
    pts = make_points()
    assert pts[0].x == 1
    assert pts[1].y == 4

"""Static gate N4 — typed named-field access.

Spec clause N4 (namedtuple-twoplane-spec.md §1.2): for `p: Point` with
`Point` declaring `x: int`, the expression `p.x` (attribute access) has
static type `int`. The attribute name must be a declared field.

Expected (from spec): typecheck + prove; `p.x` yields `int`.
"""

from typing import NamedTuple


class Point(NamedTuple):
    x: int
    y: int


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(p: Point) -> int:
    return p.x


if __name__ == "__main__":
    assert f(Point(1, 2)) == 1
    print("PASS")

"""Static gate N5 — typed positional access.

Spec clause N5 (namedtuple-twoplane-spec.md §1.3): for `p: Point` with
`Point` declaring `x: int, y: int` (in that order), the expression `p[0]` has
static type `int` (the type of field `x`), and `p[1]` has static type `int`
(the type of field `y`). The index must be an integer literal known at
type-check time (a non-literal index is a static error; an out-of-range
literal index is a static error).

Expected (from spec): typecheck + prove; `p[0]` and `p[1]` yield `int`.
"""

from typing import NamedTuple


class Point(NamedTuple):
    x: int
    y: int


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(p: Point) -> int:
    return p[0]


#@ requires True
#@ ensures True
#@ assigns \nothing
def g(p: Point) -> int:
    return p[1]


if __name__ == "__main__":
    assert f(Point(1, 2)) == 1
    assert g(Point(1, 2)) == 2
    print("PASS")

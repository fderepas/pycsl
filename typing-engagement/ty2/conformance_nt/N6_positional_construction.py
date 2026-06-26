"""Static gate N6 — typed positional construction.

Spec clause N6 (namedtuple-twoplane-spec.md §1.4): the call `Point(1, 2)`
(positional construction) is assignable to `Point` iff the number of
arguments equals the number of declared fields (minus fields with defaults,
per N1b) and each argument's type is assignable to the corresponding field's
declared type, in declaration order.

Expected (from spec): typecheck + prove; the positional call constructs a
Point.
"""

from typing import NamedTuple


class Point(NamedTuple):
    x: int
    y: int


#@ requires True
#@ ensures True
#@ assigns \nothing
def f() -> Point:
    return Point(1, 2)


if __name__ == "__main__":
    p = f()
    assert p.x == 1
    assert p[1] == 2
    print("PASS")

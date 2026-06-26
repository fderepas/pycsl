"""Static gate N4b (negative) — unknown attribute must FAIL.

Spec clause N4 (namedtuple-twoplane-spec.md §1.2): the attribute name must
be a declared field (a non-declared attribute access is a static error).

Expected (from spec): FAIL — unknown attribute is a static error.
"""

from typing import NamedTuple


class Point(NamedTuple):
    x: int
    y: int


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(p: Point) -> int:
    return p.z


if __name__ == "__main__":
    # Runtime: this raises AttributeError (no property 'z').
    try:
        f(Point(1, 2))
        print("FAIL (runtime did not raise)")
    except AttributeError:
        print("PASS (runtime AttributeError as expected)")

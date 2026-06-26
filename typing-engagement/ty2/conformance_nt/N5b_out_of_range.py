"""Static gate N5b (negative) — out-of-range index must FAIL.

Spec clause N5 (namedtuple-twoplane-spec.md §1.3): an out-of-range literal
index (`p[2]` on a 2-field Point) is a static error.

Expected (from spec): FAIL — out-of-range index is a static error.
"""

from typing import NamedTuple


class Point(NamedTuple):
    x: int
    y: int


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(p: Point) -> int:
    return p[2]


if __name__ == "__main__":
    # Runtime: this raises IndexError (plain tuple bounds).
    try:
        f(Point(1, 2))
        print("FAIL (runtime did not raise)")
    except IndexError:
        print("PASS (runtime IndexError as expected)")

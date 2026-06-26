"""Static gate N7 (negative) — wrong-arity construction must FAIL.

Spec clause N7 (namedtuple-twoplane-spec.md §1.4): a call `Point(1)` (too
few) or `Point(1, 2, 3)` (too many) is a static error (type-check failure).

Expected (from spec): FAIL — wrong arity is a static error.
"""

from typing import NamedTuple


class Point(NamedTuple):
    x: int
    y: int


#@ requires True
#@ ensures True
#@ assigns \nothing
def f() -> Point:
    return Point(1)


if __name__ == "__main__":
    # Runtime: this raises TypeError (missing positional argument).
    try:
        f()
        print("FAIL (runtime did not raise)")
    except TypeError:
        print("PASS (runtime TypeError as expected)")

"""Static gate T5 — typed key access.

Spec clause T5 (typeddict-twoplane-spec.md §1.2): for `p: Point` with
`Point` declaring `x: int`, the expression `p["x"]` has static type `int`.
The key must be a string *literal* known at type-check time (PEP 589).

Expected (from spec): typecheck + prove; `p["x"]` yields `int`.
"""

from typing import TypedDict


class Point(TypedDict):
    x: int
    y: int


#@ requires True
#@ ensures True
#@ assigns \nothing
def f(p: Point) -> int:
    return p["x"]


if __name__ == "__main__":
    assert f({"x": 1, "y": 2}) == 1
    print("PASS")

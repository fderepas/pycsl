"""Static gate T5b (negative) — unknown key must FAIL.

Spec clause T5 (typeddict-twoplane-spec.md §1.2): a subscript `p["z"]` on a
TypedDict with no declared `z` field is a static error (unknown key).

Expected (from spec): FAIL — the field `z` is not declared on `Point`.
"""

from typing import TypedDict


class Point(TypedDict):
    x: int
    y: int


#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def f(p: Point) -> int:
    # `z` is not a declared key of Point — a static error per T5.
    return p["z"]


if __name__ == "__main__":
    f({"x": 1, "y": 2})
    print("PASS")

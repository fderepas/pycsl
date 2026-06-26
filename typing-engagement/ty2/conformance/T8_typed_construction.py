"""Static gate T8 — typed construction (record literal).

Spec clause T8 (typeddict-twoplane-spec.md §1.3): the literal
`{"x": 1, "y": 2}` is assignable to `Point` iff every required key is present,
no extra key is present, and each value's type is assignable to the key's
declared type.

Expected (from spec): typecheck + prove; the dict literal constructs a Point.
"""

from typing import TypedDict


class Point(TypedDict):
    x: int
    y: int


#@ requires True
#@ ensures True
#@ assigns \nothing
def f() -> Point:
    return {"x": 1, "y": 2}


if __name__ == "__main__":
    p = f()
    assert p["x"] == 1
    print("PASS")

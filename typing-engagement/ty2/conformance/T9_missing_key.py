"""Static gate T9 (negative) — missing required key must FAIL.

Spec clause T9 (typeddict-twoplane-spec.md §1.3): a literal missing a
required key (total=True) is a static error (type-check failure).

Expected (from spec): FAIL — the construction is missing a required key.
"""

from typing import TypedDict


class Point(TypedDict):
    x: int
    y: int


#@ requires True
#@ ensures True
#@ assigns \nothing
def f() -> Point:
    # missing the required key `y` — a static error per T9.
    return {"x": 1}


if __name__ == "__main__":
    f()
    print("PASS")

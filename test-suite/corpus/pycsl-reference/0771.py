"""Test 0771 — NEGATIVE: a false projection-content claim is REJECTED.

cleared-array.md §7 negative gate (projection). `[p.x for p in a]` has the
per-index law `result[i] = get_x(a[i])`; the postcondition below falsely claims
`result[k] == a[k].y`. Because `get_x` and `get_y` are INDEPENDENT deterministic
getters, the model cannot prove `get_x(a[k]) = get_y(a[k])`, so this MUST NOT
prove (expected FAIL). A guard that the projection content law is honest — not a
vacuous/over-strong axiom that collapses distinct fields.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ ensures \forall k; 0 <= k and k < \length(\result) ==> \result[k] == a[k].y
#@ assigns \nothing
def bogus_project(a: List[Point]) -> List[int]:
    return [p.x for p in a]

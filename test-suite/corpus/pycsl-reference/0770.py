"""Test 0770 — arithmetic-over-projection comprehension is content-faithful.

cleared-array.md S2 (composed with S3). `[p.x + p.y for p in a]` lifts the
element `p.x + p.y` (arithmetic over TWO field projections of the loop target)
into the per-index law `result[i] = get_x(a[i]) + get_y(a[i])`, so a driver can
prove the exact computed contents `\result[k] == a[k].x + a[k].y`. Demonstrates
that projection composes with the pure-int arithmetic whitelist.
"""
_ = 0  # anchor
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ ensures \forall k; 0 <= k and k < \length(\result) ==> \result[k] == a[k].x + a[k].y
#@ ensures \length(\result) == \length(a)
#@ assigns \nothing
def project_sum(a: List[Point]) -> List[int]:
    return [p.x + p.y for p in a]

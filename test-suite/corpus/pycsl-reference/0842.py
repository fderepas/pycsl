"""Test 0842 — WL-04d regression lock (NEGATIVE): a FILTERED record projection is
NOT length-preserving, and NOT a per-index content map.

cleared-array §7 negative gate (filtered projection). The faithful WL-04d law for
`[p.x for p in a if p.x > 0]` gives only the length BOUND `len(result) <= len(a)`
and a membership existential — NEVER an exact length or a per-index content law,
because the result length is data-dependent (records failing `p.x > 0` are dropped,
and compaction loses the source index). This driver falsely claims the filter keeps
EVERY element in place (`\result[i] == a[i].x` at each i), which is false of real
Python whenever any `a[j].x <= 0` shifts later elements. It MUST NOT prove — a guard
that the honest under-approximation is not a vacuous / over-strong axiom.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ ensures \forall i; 0 <= i and i < \length(\result) ==> \result[i] == a[i].x
#@ assigns \nothing
def bogus_per_index(a: List[Point]) -> List[int]:
    return [p.x for p in a if p.x > 0]

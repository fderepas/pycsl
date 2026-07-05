"""Test 0806 — NEGATIVE: a false DEEPER-nested content claim is REJECTED.

nested-list.md §8/§9 EXTENSION negative gate. The depth-3 read has the faithful
content `\result == a[i][j][k]`; the postcondition below falsely claims
`a[i][j][k] + 1`. The model cannot prove
`Seq.get (Seq.get (a[i]) j) k = Seq.get (Seq.get (a[i]) j) k + 1`, so this MUST
NOT prove (expected FAIL). A guard that the deeper-nesting content law is honest
— not a vacuous / over-strong claim.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List

#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ requires 0 <= k and k < len(a[i][j])
#@ ensures \result == a[i][j][k] + 1
def bogus_deep(a: List[List[List[int]]], i: int, j: int, k: int) -> int:
    return a[i][j][k]

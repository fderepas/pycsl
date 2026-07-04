"""Test 0801 — NEGATIVE: a false nested-content claim is REJECTED.

nested-list.md §5 negative gate. The nested read has the faithful content
`\result == a[i][j]`; the postcondition below falsely claims `a[i][j] + 1`.
The model cannot prove `Seq.get (a[i]) j = Seq.get (a[i]) j + 1`, so this MUST
NOT prove (expected FAIL). A guard that the nested content law is honest — not a
vacuous/over-strong claim.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List

#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ ensures \result == a[i][j] + 1
def bogus_nested(a: List[List[int]], i: int, j: int) -> int:
    return a[i][j]

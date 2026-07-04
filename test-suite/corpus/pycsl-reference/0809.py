"""Test 0809 — NEGATIVE: a false target-dependent index claim is REJECTED.

nested-list.md §8/§9 EXTENSION negative gate. The comprehension
`[x[len(x)-1] for x in a]` yields the LAST element of each row, so the honest law
is `\result[i] == a[i][len(a[i]) - 1]`. The postcondition below falsely claims the
FIRST element `a[i][0]`. The model gives
`result[i] = Seq.get (a[i]) (Seq.length (a[i]) - 1)`, which does NOT entail
`result[i] = Seq.get (a[i]) 0` (last ≠ first in general), so this MUST NOT prove
(expected FAIL). A guard that the target-dependent index law is honest — the
lifted index is the real `len(x)-1`, not conflated with a constant `0`.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List

#@ requires \forall i; 0 <= i and i < \length(a) ==> len(a[i]) >= 1
#@ ensures \length(\result) == \length(a)
#@ ensures \forall i; 0 <= i and i < \length(a) ==> \result[i] == a[i][0]
#@ assigns \nothing
def bogus_last_col(a: List[List[int]]) -> List[int]:
    return [x[len(x) - 1] for x in a]

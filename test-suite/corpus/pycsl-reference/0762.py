"""Test 0762 — arithmetic list comprehension is content-faithful.

cleared-array.md S3. `[x + 1 for x in a]` lifts the element `x + 1` (a pure-int
term over the loop target) into the per-index law `result[i] = a[i] + 1`, so a
driver can prove the exact transformed contents — the representative of the
"element is a computed function of the source element" shape.
"""
_ = 0  # anchor
from typing import List


#@ ensures \forall k; 0 <= k and k < \length(\result) ==> \result[k] == a[k] + 1
#@ ensures \length(\result) == \length(a)
#@ assigns \nothing
def incr_all(a: List[int]) -> List[int]:
    return [x + 1 for x in a]

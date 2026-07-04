"""Test 0786 — NEGATIVE: a false dict-comprehension value claim is REJECTED.

cleared-array.md item 3 negative gate. `{x: x + 1 for x in a}` has the per-source
law `Map.get result (a[i]) = Some (a[i] + 1)`. The postcondition below falsely
claims `\map_get(\result, a[k]) == a[k] + 2`. The model proves the value is
`a[k] + 1`, contradicting `a[k] + 2`, so this MUST NOT prove (expected FAIL). A
guard that the dict content law is honest — not vacuous/over-strong.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List, Dict


#@ ensures \forall k; 0 <= k and k < \length(a) ==> \map_get(\result, a[k]) == a[k] + 2
#@ assigns \nothing
def bogus_incr_dict(a: List[int]) -> Dict[int, int]:
    return {x: x + 1 for x in a}

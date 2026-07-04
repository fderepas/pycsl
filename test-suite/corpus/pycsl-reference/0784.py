"""Test 0784 — NEGATIVE: a false call-comprehension content claim is REJECTED.

cleared-array.md item 1 negative gate. `[g(x) for x in a]` has the per-index law
`result[i] = g(a[i])`. The postcondition below falsely claims
`result[k] == g(a[k]) + 1`. Since `g` is a deterministic `let function`, the
model proves `result[k] = g(a[k])`, which contradicts `= g(a[k]) + 1`, so this
MUST NOT prove (expected FAIL). A guard that the call content law is honest —
not a vacuous/over-strong claim.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


#@ ensures \result == 2 * x + 1
#@ assigns \nothing
def g(x: int) -> int:
    return 2 * x + 1


#@ ensures \forall k; 0 <= k and k < \length(\result) ==> \result[k] == g(a[k]) + 1
#@ assigns \nothing
def bogus_map_g(a: List[int]) -> List[int]:
    return [g(x) for x in a]

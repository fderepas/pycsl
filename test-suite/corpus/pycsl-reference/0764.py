"""Test 0764 — NEGATIVE: a false content claim about a comprehension is REJECTED.

cleared-array.md §7 negative gate. `[x for x in a]` has the per-index law
`result[i] = a[i]`; the postcondition below falsely claims `result[i] = a[i] + 1`.
The content model is honest, so this MUST NOT prove (expected FAIL) — a guard
that the comprehension law is not a vacuous/over-strong axiom.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


#@ ensures \forall k; 0 <= k and k < \length(\result) ==> \result[k] == a[k] + 1
#@ assigns \nothing
def bogus_copy(a: List[int]) -> List[int]:
    return [x for x in a]

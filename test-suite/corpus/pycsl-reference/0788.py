"""Test 0788 — NEGATIVE: a false set-comprehension membership claim is REJECTED.

cleared-array.md item 3 negative gate. `{x + 1 for x in a}` has the membership
law `Map.get result (a[i] + 1) = Some 0` (the TRANSFORMED element is present).
The postcondition below falsely claims the ORIGINAL element `a[k]` is a member.
The set contains `a[k] + 1`, and nothing forces `a[k]` itself to be present, so
the model cannot prove `\has_key(\result, a[k])` — this MUST NOT prove (expected
FAIL). A guard that the set membership law is honest — an under-approximation
that never over-claims the domain.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List


#@ ensures \forall k; 0 <= k and k < \length(a) ==> \has_key(\result, a[k])
#@ assigns \nothing
def bogus_incr_set(a: List[int]) -> set:
    return {x + 1 for x in a}

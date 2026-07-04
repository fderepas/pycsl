"""Test 0787 — set comprehension is content-faithful.

cleared-array.md item 3. `{x + 1 for x in a}` now lowers to a `map int (option
int)` (the set model, present = `Some 0`) with the membership law
`forall i. Map.get result (a[i] + 1) = Some 0` — every produced element is
present. So a driver can prove each transformed source element is a member of the
result (`\has_key`), which the old opaque `set_comp` could not express. Sound
under-approximation of the set (says nothing about ABSENT elements). No global
axiom.
"""
_ = 0  # anchor
from typing import List


#@ ensures \forall k; 0 <= k and k < \length(a) ==> \has_key(\result, a[k] + 1)
#@ assigns \nothing
def incr_set(a: List[int]) -> set:
    return {x + 1 for x in a}

"""Test 0785 — dict comprehension is content-faithful.

cleared-array.md item 3. `{x: x + 1 for x in a}` (an IDENTITY key with a pure-int
value) now lowers to a `map int (option int)` with the per-source membership law
`forall i. Map.get result (a[i]) = Some (a[i] + 1)` — so a driver can prove each
source element is a KEY of the result (`\has_key`) AND maps to the transformed
value (`\map_get`), which the old opaque `dict_comp` could not express.

Soundness pin: the key is the identity, so colliding sources map to the SAME key
and (value being a deterministic function of the key) the SAME value — insertion
order is irrelevant, and the per-source law is sound. It is an under-approximation
of the domain (says nothing about keys not in `a`). No global axiom.
"""
_ = 0  # anchor
from typing import List, Dict


#@ ensures \forall k; 0 <= k and k < \length(a) ==> \has_key(\result, a[k])
#@ ensures \forall k; 0 <= k and k < \length(a) ==> \map_get(\result, a[k]) == a[k] + 1
#@ assigns \nothing
def incr_dict(a: List[int]) -> Dict[int, int]:
    return {x: x + 1 for x in a}

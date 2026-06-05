"""Test 0526 — dict string KEYS are first-class (no-more-int-3 A1 / Track 1, T1.2).

A `Dict[str, int]` key type is a real Why3 `string` (κ = string), not hashed to
an opaque int. With real string keys, two *distinct* keys (`k1 != k2`) are
provably non-aliasing, so writing `k2` does not disturb the `k1` entry: after
`d[k1] = v1; d[k2] = v2`, the read `d[k1]` is `v1`.

Before T1.2 a runtime string key was hashed to an opaque int (`str_hash(k1)` vs
`str_hash(k2)` unconstrained — `k1 != k2` does NOT imply the hashes differ, since
hashing is not injective), so the prover could not exclude a collision and this
was unprovable. (Distinct string *literals* hash to distinct compile-time
constants, so they already worked — the gap is runtime keys.) Flips to PASS when
T1.2 threads the key type κ (map `string` keys, decidable equality) and stops
hashing string keys.
"""
_ = 0  # anchor
from typing import Dict


#@ requires k1 != k2
#@ ensures \result == v1
#@ assigns \nothing
#@ no_exception KeyError
def distinct_keys(k1: str, k2: str, v1: int, v2: int) -> int:
    d: Dict[str, int] = {}
    d[k1] = v1
    d[k2] = v2
    return d[k1]

"""Test 0755 — cleared-hash.md S7: distinct-key non-aliasing on an UN-ANNOTATED local.

An un-annotated dict local (`d = {}`) written with string keys is inferred string-keyed
(κ = string, cleared-hash.md S1) and lowers to `map string (option ν)` with native, injective
`String.(=)` — NOT `map int` + the opaque `str_hash_op`. So two DISTINCT keys (`k1 != k2`) are
provably non-aliasing: after `d[k1] = v1; d[k2] = v2`, the read `d[k1]` is still `v1` (writing
`k2` cannot disturb the `k1` entry).

UNPROVABLE under the opaque-hash model: `str_hash_op` is a bodyless `val`, so `k1 != k2` does NOT
imply `str_hash_op k1 != str_hash_op k2` (hashing is not injective) — the prover must admit a
collision under which `d[k2]=v2` clobbers `d[k1]`. Native string keys remove that collision."""
_ = 0  # anchor
#@ requires k1 != k2
#@ ensures \result == v1
#@ assigns \nothing
#@ no_exception KeyError
def distinct_keys_local(k1: str, k2: str, v1: int, v2: int) -> int:
    d = {}
    d[k1] = v1
    d[k2] = v2
    return d[k1]

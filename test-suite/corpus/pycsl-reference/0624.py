"""Test 0624 — two-binder dict-items quantification (07-1311 Q3).

`\\forall k, v in d.items(); P(k, v)` binds the key AND value of every present entry, lowering to
`forall k. match Map.get d k with Some v -> P | None -> true end` over the map+option model.
"""
# pycsl-flags: --memory-model hoare


#@ ensures \forall k, v in d.items(); (k > 0) ==> (v == v)
#@ assigns \nothing
def h(d: dict) -> int:
    return 0

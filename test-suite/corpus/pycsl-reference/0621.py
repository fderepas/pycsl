"""Test 0621 — quantification over dict keys and values (07-1311 Q2/Q3).

`\\forall k in d;` and `\\forall k in d.keys();` range over the present keys (desugar to the
map-presence guard `Map.get d k <> None`). `\\forall v in d.values();` ranges over stored values
(`exists k. Map.get d k = Some v`) — quantification over map values, previously unexpressible.
"""
# pycsl-flags: --memory-model hoare


#@ ensures \forall k in d; k == k
#@ ensures \forall k in d.keys(); k == k
#@ ensures \forall v in d.values(); v == v
#@ assigns \nothing
def h(d: dict) -> int:
    return 0

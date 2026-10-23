"""Test 0820 — WL-05b regression lock (POSITIVE): dict-PARAM item-mutation PROVES.

wrong-lowering-to-fix.md §WL-05b (FAITHFUL caller-visible dict/set param mutation).
An item-mutation `d[k] = v` of a `Dict[...]` PARAMETER is now FAITHFULLY SUPPORTED.
Python passes dicts by reference, so the write must be VISIBLE to the caller — the
emitter models an inner-mutated dict param as a caller-visible MUTABLE
`ref (map string (option int))` with a sound `writes {d}` frame, exactly the shape the
SMT-feasibility spike proves on Alt-Ergo + Z3
(test-suite/corpus/conformance/spikes/wl05b_param_mut_spike.mlw). The write lowers to
`d := map_update_some !d k v` and the read-back to `Map.get !d k` — UNIFORMLY through
the ref (the WL-05 bug was the inconsistent `d :=`/bare-`d` mix, now gone). After
`d["a"] = 5`, reading `d["a"]` yields `5` — this write-read-back on a param dict
PROVES. Caller-visibility across functions is locked by 0832. This driver was a
NEGATIVE rejection lock under WL-05; WL-05b converts it to POSITIVE.
"""
_ = 0  # anchor
from typing import Dict


#@ ensures \result == 5
def mutate_dict_param(d: Dict[str, int]) -> int:
    d["a"] = 5
    return d["a"]

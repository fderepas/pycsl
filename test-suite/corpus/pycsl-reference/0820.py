"""Test 0820 — WL-05 regression lock (NEGATIVE): dict-PARAM item-mutation is REJECTED. # pycsl-expected: FAIL

wrong-lowering-to-fix.md §WL-05. An item-mutation `d[k] = v` of a `Dict[...]`
PARAMETER is out of scope. Python passes dicts by reference, so the write must be
VISIBLE to the caller — a faithful model needs a caller-visible mutation frame
(`writes {d}`) on a mutable-map param, the SAME hard problem for which RECORD-param
mutation (static-ref ‡) and LIST inner mutation (nested-list-mutable) are documented
out of scope. The by-value `map string (option int)` param is NOT a `ref`, so the old
lowering emitted internally-inconsistent WhyML (`d := map_update_some !d k v` — `:=`/`!d`
on a non-ref, then a bare `Map.get d k` read) that fails Why3's type-check. The fix
REJECTS it cleanly with a clear diagnostic (`PYCSL-WHYML-PARAM-COLLECTION-MUT`) instead
of emitting broken WhyML. This driver locks the rejection: it must NOT produce a
"Verification SUCCESS" (a raised PIPELINE ERROR ⇒ XFAIL). The faithful path is to
mutate a LOCAL dict (0822 proves) or RETURN the updated dict.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Dict


#@ ensures \result == 5
def mutate_dict_param(d: Dict[str, int]) -> int:
    d["a"] = 5
    return d["a"]

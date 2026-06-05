"""Test 0523 — dict string VALUES carry content (no-more-int-3 A1 / Track 1, T1.1).

A `Dict[int, str]` value type should be a real Why3 `string` (ν = string), not coerced to int.
After `d[k] = s`, the value read back `d[k]` is the same string, so `\str_length(d[k]) ==
\str_length(s)` proves — string values carry content through a dict. Before A1, the parsed
`Dict[K, V]` element types were discarded (`_get_type_name` → bare `dict`) and the value was a
hashed `int`, so the WhyML was ill-typed (`map_update_some … (v: int)` fed a `string`) and this
was unprovable.

Flips to PASS when A1 T1.1 threads the value type ν through the dict path (map type, MapGet's
typed missing-key default `None -> ""`, MapSet, dict-literal lowering) and stops `_coerce_to_int`
on a known-string value. Key type (T1.2) and non-int/non-string values are separate sub-stages.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Dict


#@ requires \str_length(s) >= 1
#@ ensures \str_length(\result) == \str_length(s)
#@ assigns \nothing
def store_and_read(k: int, s: str) -> str:
    d: Dict[int, str] = {}
    d[k] = s
    return d[k]

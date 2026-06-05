"""Test 0532 — nested-dict values (A1-residual nested-map; A4 JObj enabler).

`Dict[str, Dict[int, int]]` value should be a real nested `map int (option int)`,
not collapsed to int, and `d[ko][ki]` (double subscript) should read through both
maps. Fails today: the inner value collapses to int and `d[ko][ki]` falls to the
opaque `subscript_get`. Flips when ν threads a nested map + double-subscript lowers
to nested `Map.get`.
"""
_ = 0  # anchor
from typing import Dict


#@ ensures \result == 5
#@ assigns \nothing
#@ no_exception KeyError
def nested_get(ko: str, ki: int) -> int:
    d: Dict[str, Dict[int, int]] = {}
    inner: Dict[int, int] = {}
    inner[ki] = 5
    d[ko] = inner
    return d[ko][ki]

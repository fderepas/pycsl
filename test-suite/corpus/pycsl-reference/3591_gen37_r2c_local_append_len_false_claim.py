r"""Test 3591 — gen #37 r2c-wall R2c-local (expected FAIL).

False twin of 3590: `len(..) == 0` after one append (CPython: 1) must NOT prove.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def w_len1_twin(n: int) -> int:
    generics: Dict[str, PyVal] = {}
    t: str = "G"
    if t not in generics:
        generics[t] = {"kind": "class", "methods": []}
    generics[t]["methods"].append({"name": "m"})
    return len(generics[t]["methods"])

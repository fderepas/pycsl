r"""Test 3595 — gen #37 r2c-wall R2c-local (expected FAIL).

False twin of 3594: claims the OLD value is still read (CPython: "fn") must NOT prove.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def w_store_twin(n: int) -> int:
    g: Dict[str, PyVal] = {}
    g["G"] = {"kind": "class", "methods": []}
    g["G"]["kind"] = "fn"
    if g["G"]["kind"] == "fn":
        return 1
    return 0

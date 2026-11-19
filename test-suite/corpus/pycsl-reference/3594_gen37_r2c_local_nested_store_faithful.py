r"""Test 3594 — gen #37 r2c-wall R2c-local (expected PASS).

R2c-local: nested store `g["G"]["kind"] = "fn"` on a literal-built local tree, read back `== "fn"` PROVES.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def w_store(n: int) -> int:
    g: Dict[str, PyVal] = {}
    g["G"] = {"kind": "class", "methods": []}
    g["G"]["kind"] = "fn"
    if g["G"]["kind"] == "fn":
        return 1
    return 0

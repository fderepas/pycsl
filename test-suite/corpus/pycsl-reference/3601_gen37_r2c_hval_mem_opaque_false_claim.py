r"""Test 3601 — gen #37 r2c-wall R2c-local (expected FAIL).

`func in g["G"]["methods"]` right after appending func is True in CPython (identity), so `\result == 0` is FALSE; the hval-needle membership is the UNINTERPRETED `hval_mem_opaque` (no axiom) and must NOT decide it.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List

PyVal = Any


#@ requires len(funcs) >= 1
#@ ensures \result == 0
#@ assigns \nothing
def w_mem_opaque_false(funcs: List[Dict[str, PyVal]]) -> int:
    g: Dict[str, PyVal] = {}
    g["G"] = {"methods": []}
    for func in funcs:
        g["G"]["methods"].append(func)
        if func in g["G"]["methods"]:
            return 1
    return 0

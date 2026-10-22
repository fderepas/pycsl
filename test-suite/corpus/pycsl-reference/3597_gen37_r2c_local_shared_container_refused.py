r"""Test 3597 — gen #37 r2c-wall R2c-local (expected FAIL).

REFUSAL: `generics["G"] = func` (a parameter element) then `generics["G"]["methods"].append(1)` mutates the CALLER's object; refused (non-literal container on the written path).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def refuse_partner_store(funcs: List[Dict[str, PyVal]]) -> int:
    generics: Dict[str, PyVal] = {}
    for func in funcs:
        generics["G"] = func
        generics["G"]["methods"].append(1)
    return 0

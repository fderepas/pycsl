r"""Test 3600 — gen #37 r2c-wall R2c-local (expected PASS).

R2c-local make-or-break driver `cgd_min` (review §5): the `_collect_generic_decls` loop shape over a `List[Dict[str, PyVal]]` with the local append is emitted, L3-tc clean, and proves its type-safety+frame contract. At base the append was refused (#280).
"""
# pycsl-expected: PASS
from typing import Any, Dict, List

PyVal = Any


#@ requires True
#@ ensures True
#@ assigns \nothing
def cgd_min(funcs: List[Dict[str, PyVal]]) -> Dict[str, PyVal]:
    generics: Dict[str, PyVal] = {}
    for func in funcs:
        t: str = func.get("self_type") or ""
        if t == "G":
            if t not in generics:
                generics[t] = {"kind": "class", "methods": []}
            generics[t]["methods"].append(func)
    return generics

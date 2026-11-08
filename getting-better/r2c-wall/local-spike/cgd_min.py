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

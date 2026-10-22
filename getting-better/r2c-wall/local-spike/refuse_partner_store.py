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

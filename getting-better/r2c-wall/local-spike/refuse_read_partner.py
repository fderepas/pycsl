from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def refuse_read_partner(n: int) -> int:
    generics: Dict[str, PyVal] = {}
    generics["G"] = {"methods": []}
    x: Dict[str, PyVal] = generics["G"]
    generics["G"]["methods"].append(1)
    return len(x["methods"])

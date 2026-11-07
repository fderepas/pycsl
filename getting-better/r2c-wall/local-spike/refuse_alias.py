from typing import Any, Dict, List

PyVal = Any


#@ ensures True
#@ assigns \nothing
def refuse_alias(n: int) -> Dict[str, PyVal]:
    generics: Dict[str, PyVal] = {}
    other: Dict[str, PyVal] = generics
    generics["G"] = {"methods": []}
    generics["G"]["methods"].append(1)
    return other

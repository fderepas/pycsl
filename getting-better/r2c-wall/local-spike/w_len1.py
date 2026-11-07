from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def w_len1(n: int) -> int:
    generics: Dict[str, PyVal] = {}
    t: str = "G"
    if t not in generics:
        generics[t] = {"kind": "class", "methods": []}
    generics[t]["methods"].append({"name": "m"})
    return len(generics[t]["methods"])

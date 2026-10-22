from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def g(d: Dict[str, Dict[str, PyVal]]) -> int:
    n = 0
    for k, v in d.items():
        if v.get("a") == "x":
            n = 1
    return n

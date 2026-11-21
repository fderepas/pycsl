from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def g(d: Dict[str, PyVal]) -> int:
    x = d.get("t")
    if bool(x):
        if not x:
            return 1
    return 0

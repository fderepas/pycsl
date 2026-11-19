from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"t": "x"}
    if bool(d.get("t")):
        return 1
    return 2

from typing import Any, Dict

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"s": "abc"}
    return len(d.get("s"))

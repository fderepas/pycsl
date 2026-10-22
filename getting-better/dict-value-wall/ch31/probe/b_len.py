from typing import Any, Dict

PyVal = Any


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"s": "abc"}
    return len(d.get("s"))

from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def g(d: Dict[str, PyVal]) -> int:
    n = d.get("name")
    s = f"{n}"
    if s == "0":
        return 1
    return 2

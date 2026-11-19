from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"flag": True}
    n = d.get("flag")
    s = f"{n}"
    if s == "1":
        return 1
    return 2

from typing import Any, Dict

PyVal = Any


#@ ensures \result == "0!"
#@ assigns \nothing
def g() -> str:
    d: Dict[str, PyVal] = {"n": "ab"}
    n = d.get("n")
    return f"{n}!"

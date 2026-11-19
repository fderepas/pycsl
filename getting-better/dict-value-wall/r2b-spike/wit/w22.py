from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def has_loc() -> bool:
    rec: Dict[str, PyVal] = {"term": {"loc": 3, "x": 1}}
    inner = rec.get("term") or {}
    return "loc" in inner

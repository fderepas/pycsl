from typing import Any, Dict

PyVal = Any

#@ ensures \result == False
#@ assigns \nothing
def in_str() -> bool:
    rec: Dict[str, PyVal] = {"s": "abc"}
    s = rec.get("s")
    return "b" in s

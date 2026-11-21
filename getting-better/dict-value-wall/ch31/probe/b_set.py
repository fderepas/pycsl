from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"xs": ["a", "b"]}
    s = set(d.get("xs") or [])
    if "a" in s:
        return 1
    return 2

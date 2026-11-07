from typing import Any, Dict

PyVal = Any


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"xs": ["a", "b"]}
    s = list(d.get("xs") or [])
    return len(s)

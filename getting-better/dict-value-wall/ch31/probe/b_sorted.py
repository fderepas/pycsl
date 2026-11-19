from typing import Any, Dict

PyVal = Any


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    d: Dict[str, PyVal] = {"xs": ["b", "a"]}
    n = 0
    for x in sorted(d.get("xs", [])):
        n = n + 1
    return n

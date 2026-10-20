from typing import Any, Dict

PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def count_str() -> int:
    rec: Dict[str, PyVal] = {"s": "abc"}
    n = 0
    for c in rec.get("s", []):
        n = n + 1
    return n

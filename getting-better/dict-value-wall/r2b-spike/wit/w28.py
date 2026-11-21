from typing import Any, Dict

PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def count_dict() -> int:
    rec: Dict[str, PyVal] = {"d": {"a": 1}}
    n = 0
    for k in rec.get("d", []):
        n = n + 1
    return n

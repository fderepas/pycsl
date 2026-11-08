from typing import Any, Dict
PyVal = Any

#@ assigns \nothing
def count_valid(rec: Dict[str, PyVal]) -> int:
    n = 0
    for r in (rec.get("records") or []):
        if r.get("answer") == "Valid":
            n = n + 1
    return n

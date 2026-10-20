from typing import Any, Dict
PyVal = Any

#@ assigns \nothing
def n_keys(rec: Dict[str, PyVal]) -> int:
    n = 0
    for k in rec.keys():
        n = n + 1
    return n

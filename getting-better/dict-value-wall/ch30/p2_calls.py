from typing import Any, Dict, List

PyVal = Any

#@ requires True
#@ ensures True
#@ assigns \nothing
def is_valid(rec: Dict[str, PyVal]) -> bool:
    return rec.get("answer") == "Valid"

#@ requires True
#@ ensures True
#@ assigns \nothing
def count_valid(recs: List[Dict[str, PyVal]]) -> int:
    c = 0
    for r in recs:
        if is_valid(r):
            c += 1
    return c

#@ requires True
#@ ensures True
#@ assigns \nothing
def through(recs: List[Dict[str, PyVal]]) -> int:
    return count_valid(recs)

#@ requires True
#@ ensures True
#@ assigns \nothing
def from_holder(holder: Dict[str, PyVal]) -> int:
    return count_valid(holder.get("records", []))

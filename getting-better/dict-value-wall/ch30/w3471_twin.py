from typing import Any, Dict, List

PyVal = Any

#@ ensures \result != False ==> "answer" in rec
#@ assigns \nothing
def is_valid(rec: Dict[str, PyVal]) -> bool:
    a = rec.get("answer")
    return a == "Valid"

#@ ensures \result == 0
#@ assigns \nothing
def none_valid() -> int:
    holder: Dict[str, PyVal] = {"records": [{"x": "Valid"}, {"answer": "Valid"}]}
    for r in holder.get("records", []):
        if is_valid(r):
            return 1
    return 0

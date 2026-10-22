from typing import Any, Dict, List
PyVal = Any

#@ ensures \result == len(fns)
#@ assigns \nothing
def cnt(fns: List[Dict[str, PyVal]]) -> int:
    return len(fns)

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    holder: Dict[str, PyVal] = {"records": [*({"b": 1}, {"c": 1}), {"a": 1}]}
    return cnt(holder.get("records", []))

if __name__ == "__main__":
    assert g() == 2, g()

from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def has_name() -> bool:
    rec: Dict[str, PyVal] = {"names": ["a", "x"]}
    names = rec.get("names") or []
    return "z" in names

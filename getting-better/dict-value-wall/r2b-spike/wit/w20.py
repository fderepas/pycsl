from typing import Any, Dict

PyVal = Any

#@ ensures \result == "yes" or \result == "none"
#@ assigns \nothing
def find_last() -> str:
    rec: Dict[str, PyVal] = {"fns": [{"name": "b", "k": "y"}, {"name": "c", "k": "z"}]}
    for f in rec.get("fns", []):
        if f.get("k") == "z":
            if f.get("name") == "c":
                return "yes"
            return "no"
    return "none"

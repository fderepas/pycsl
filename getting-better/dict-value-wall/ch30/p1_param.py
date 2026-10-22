from typing import Any, Dict, List

PyVal = Any

#@ ensures \result != False ==> True
#@ assigns \nothing
def has_named_c(fns: List[Dict[str, PyVal]]) -> bool:
    for f in fns:
        if f.get("name") == "c":
            return True
    return False

from typing import Any, Dict, List

PyVal = Any

#@ ensures \result == 0
#@ assigns \nothing
def recheck(fns: List[Dict[str, PyVal]]) -> int:
    for f in fns:
        if f.get("name") == "c":
            if not (f.get("name") == "c"):
                return 1
    return 0

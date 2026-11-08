from typing import Any, Dict, List

PyVal = Any

#@ assigns \nothing
def rebind(fns: List[Dict[str, PyVal]]) -> int:
    fns = []
    return len(fns)

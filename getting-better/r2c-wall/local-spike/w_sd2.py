from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 2
#@ assigns \nothing
def w_sd2(n: int) -> int:
    by: Dict[str, PyVal] = {}
    by.setdefault("a", []).append("x")
    by.setdefault("a", []).append("y")
    return len(by["a"])

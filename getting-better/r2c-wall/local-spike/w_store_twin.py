from typing import Any, Dict, List

PyVal = Any


#@ ensures \result == 0
#@ assigns \nothing
def w_store_twin(n: int) -> int:
    g: Dict[str, PyVal] = {}
    g["G"] = {"kind": "class", "methods": []}
    g["G"]["kind"] = "fn"
    if g["G"]["kind"] == "fn":
        return 1
    return 0

from typing import Any, Dict, List

PyVal = Any

#@ assigns \nothing
def build(x: PyVal) -> int:
    g: Dict[str, PyVal] = {"methods": []}
    g["methods"].append(x)
    return len(g["methods"])

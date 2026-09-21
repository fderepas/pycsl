from __future__ import annotations
from typing import Dict


class PyVal:
    pass


#@ ensures \result == 1
def probe() -> int:
    d: Dict[str, PyVal] = {}
    d["a"] = 0
    v = d.get("zzz")
    if v == d["a"]:
        return 1
    return 2

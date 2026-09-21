from __future__ import annotations
from typing import Dict


class PyVal:
    pass


#@ ensures \result == 1
def probe() -> int:
    d: Dict[str, PyVal] = {}
    v = d.get("zzz")
    if isinstance(v, int):
        return 1
    return 2

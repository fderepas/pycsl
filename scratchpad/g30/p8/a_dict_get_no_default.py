from typing import Dict


#@ ensures \result == 1
def probe() -> int:
    d: Dict[str, int] = {}
    v = d.get("k")
    if v == 0:
        return 1
    return 2

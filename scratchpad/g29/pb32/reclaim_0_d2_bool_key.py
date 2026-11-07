from typing import Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[int, int] = {}
    d[1] = 10
    d[True] = 20
    return d[1]

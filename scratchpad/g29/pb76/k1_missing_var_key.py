from typing import Dict
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[int, int] = {1: 10}
    k: int = 2
    return d[k] * 0

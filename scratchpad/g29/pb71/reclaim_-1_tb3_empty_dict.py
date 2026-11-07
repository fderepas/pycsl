from typing import Dict
_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    d: Dict[int, int] = {}
    if d:
        return 1
    return 0

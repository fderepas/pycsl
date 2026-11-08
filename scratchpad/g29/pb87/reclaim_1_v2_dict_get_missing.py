from typing import Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    d: Dict[int, int] = {1: 10}
    return d.get(2, 99)

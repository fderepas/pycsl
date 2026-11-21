from typing import Dict
_ = 0  # anchor


#@ ensures \result == -9
def probe() -> int:
    d: Dict[int, int] = {1: 10, 1: 20}
    return d[1] - 19

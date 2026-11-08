from typing import Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[int, int] = {1: 10, 2: 20}
    s: int = 0
    for k, v in d.items():
        s = s + k * v
    return s

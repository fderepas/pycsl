from typing import Dict
_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    d: Dict[int, int] = {1: 10}
    v: int = d.setdefault(2, 7)
    return v

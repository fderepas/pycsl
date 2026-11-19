from typing import Tuple
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    t: Tuple[int, int] = (7, 8)
    return t[0]

from typing import Tuple
_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    t: Tuple[int, int] = (7, 8)
    return t[0]

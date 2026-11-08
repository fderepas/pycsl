from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [3, 1, 2]
    ys: List[int] = sorted(xs)
    return ys[0]

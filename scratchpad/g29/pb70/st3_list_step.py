from typing import List
_ = 0  # anchor


#@ ensures \result == 4
def probe() -> int:
    xs: List[int] = [1, 2, 3, 4]
    ys: List[int] = xs[::2]
    return len(ys)

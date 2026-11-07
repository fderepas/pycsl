from typing import List
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = [1, 2]
    ys: List[int] = xs
    ys[0] = 9
    return xs[0]

from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1, 2]
    ys: List[int] = xs
    ys[0] = 9
    return xs[0]

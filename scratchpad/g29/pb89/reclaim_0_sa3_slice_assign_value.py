from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    xs[1:] = [9]
    return xs[1]

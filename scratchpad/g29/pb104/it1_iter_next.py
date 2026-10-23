from typing import List
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [5, 6]
    it = iter(xs)
    return next(it)

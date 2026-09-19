from typing import List
_ = 0  # anchor


#@ no_exception StopIteration
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = []
    it = iter(xs)
    next(it)
    return 0

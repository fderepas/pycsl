from typing import List
_ = 0  # anchor


#@ no_exception \all
#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1]
    return xs[5] * 0

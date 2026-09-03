from typing import List

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def driver() -> int:
    xs: List[int] = [0, 7]
    xs.sort(reverse=True)
    return xs[0]

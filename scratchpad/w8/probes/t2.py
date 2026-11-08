from typing import List

#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f(ys: List[int]) -> int:
    xs: List[int] = [1, 2]
    xs = ys
    return xs[0]

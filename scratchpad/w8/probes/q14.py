from typing import List

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2, 3]
    ys: List[int] = [x for x in xs if x > 10]
    return ys[0]

from typing import List

#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2, 3]
    del xs[0]
    return xs[0]

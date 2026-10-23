from typing import List, Dict

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2, 3]
    xs[0] += 5
    return xs[0] - 6

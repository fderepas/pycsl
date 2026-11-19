from typing import List

#@ requires len(a) >= 2
#@ requires a[0] == 0.1
#@ requires a[1] == 0.2
#@ ensures \result == 0.3
#@ assigns \nothing
def f(a: List[float]) -> float:
    return a[0] + a[1]

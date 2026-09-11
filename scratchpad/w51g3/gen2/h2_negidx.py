from typing import List

#@ requires len(a) == 2
#@ requires a[0] == 7
#@ ensures \result == 7
#@ assigns \nothing
def f(a: List[int]) -> int:
    return a[-1]

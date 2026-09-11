from typing import List

#@ requires len(a) == 2
#@ requires a[1] == 9
#@ ensures \result == 9
#@ assigns \nothing
def f(a: List[int]) -> int:
    return a[-1]

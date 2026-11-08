from typing import List


#@ requires True
#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    a: List[int] = [3, 1, 2]
    b: List[int] = a
    b.sort()
    return a[0]

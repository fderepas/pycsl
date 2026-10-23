from typing import List


#@ requires True
#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    a: List[int] = [1, 2, 3]
    b: List[int] = a
    b.reverse()
    return a[0]

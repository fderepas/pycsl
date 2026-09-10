_ = 0  # anchor
from typing import List


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    a: List[int] = [1]
    b: List[int] = a
    b[0] = 2
    return a[0]

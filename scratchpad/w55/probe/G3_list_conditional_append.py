# pycsl-flags: --memory-model hoare
from typing import List


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f(c: int) -> int:
    xs: List[int] = [1]
    if c > 0:
        xs.append(2)
    return len(xs)

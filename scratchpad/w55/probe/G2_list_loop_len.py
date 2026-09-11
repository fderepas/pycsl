# pycsl-flags: --memory-model hoare
from typing import List


#@ requires n > 0
#@ ensures \result == 1
#@ assigns \nothing
def f(n: int) -> int:
    xs: List[int] = []
    #@ loop invariant 0 <= i <= n
    #@ loop variant n - i
    for i in range(n):
        xs.append(i)
    return len(xs)

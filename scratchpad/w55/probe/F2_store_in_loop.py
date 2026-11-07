# pycsl-flags: --memory-model hoare
from typing import Dict


#@ requires n > 0
#@ ensures \result == 1
#@ assigns \nothing
def f(n: int) -> int:
    d: Dict[int, int] = {}
    #@ loop invariant 0 <= i <= n
    #@ loop variant n - i
    for i in range(n):
        d[i] = i
    return len(d)

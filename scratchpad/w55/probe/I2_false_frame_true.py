# pycsl-flags: --memory-model hoare
from typing import List


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def g(a: List[int]) -> int:
    a[0] = 9
    return 0


#@ requires a[0] == 1
#@ ensures \result == 9
#@ assigns \nothing
def f(a: List[int]) -> int:
    g(a)
    return a[0]

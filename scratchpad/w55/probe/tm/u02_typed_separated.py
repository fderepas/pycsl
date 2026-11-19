# pycsl-flags: --memory-model typed
from typing import List

#@ requires \separated(a, 1, b, 1)
#@ requires a[0] == 1
#@ ensures \result == 1
#@ assigns b[0..0]
def f(a: List[int], b: List[int]) -> int:
    b[0] = 9
    return a[0]

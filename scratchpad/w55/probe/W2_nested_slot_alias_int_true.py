# pycsl-flags: --memory-model hoare
from typing import List

_ = 0
#@ ensures \result == 9
#@ assigns \nothing
def f() -> int:
    a: List[List[int]] = [[1], [2]]
    a[0] = a[1]
    a[0][0] = 9
    return a[1][0]

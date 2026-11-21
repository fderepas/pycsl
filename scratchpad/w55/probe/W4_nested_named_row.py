# pycsl-flags: --memory-model hoare
from typing import List

_ = 0
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    row: List[int] = [2]
    a: List[List[int]] = [[1], row]
    row[0] = 9
    return a[1][0]

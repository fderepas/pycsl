# pycsl-flags: --memory-model typed
from typing import List

_ = 0
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: List[int] = [1]
    b = a
    b[0] = 9
    return a[0]

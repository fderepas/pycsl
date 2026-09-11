# pycsl-flags: --memory-model hoare
from typing import List

_ = 0
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    a: List[int] = [1, 2]
    a += [3]
    return len(a)

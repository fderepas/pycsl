# pycsl-flags: --memory-model hoare
from typing import List

_ = 0
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1]
    xs.append(2)
    return len(xs)

# pycsl-flags: --memory-model hoare
from typing import List

_ = 0
#@ no_exception ValueError
#@ ensures True
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2]
    return xs.index(5)

# pycsl-flags: --memory-model hoare
from typing import List

_ = 0
#@ no_exception IndexError
#@ ensures True
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2]
    return xs[-5]

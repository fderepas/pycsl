# pycsl-flags: --memory-model hoare
from typing import Dict, List

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    a: List[List[int]] = [[1]]
    return a[0][5]

# pycsl-flags: --memory-model hoare
from typing import List

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    xs: List[int] = []
    for x in xs:
        return x
    return 0

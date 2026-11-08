# pycsl-flags: --memory-model hoare
from typing import Dict, List

_ = 0
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 1}
    return d.get(5, 0)

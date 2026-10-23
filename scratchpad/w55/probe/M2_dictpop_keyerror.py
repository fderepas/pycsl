# pycsl-flags: --memory-model hoare
from typing import Dict

_ = 0
#@ no_exception KeyError
#@ ensures True
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 1}
    return d.pop(5)

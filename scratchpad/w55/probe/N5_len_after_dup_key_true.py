# pycsl-flags: --memory-model hoare
from typing import Dict

_ = 0
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 1}
    d[1] = 2
    return len(d)

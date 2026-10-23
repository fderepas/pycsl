# pycsl-flags: --memory-model hoare
from typing import Dict

_ = 0
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {1: 1}
    d[True] = 2
    return len(d)

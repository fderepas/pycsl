# pycsl-flags: --memory-model hoare
from typing import Dict

_ = 0
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {}
    d[1] = 1
    if d:
        return 7
    return 0

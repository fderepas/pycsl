# pycsl-flags: --memory-model hoare
from typing import Dict

_G: Dict[int, int] = {1: 1}


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    d = _G
    d[1] = 2
    return _G[1]

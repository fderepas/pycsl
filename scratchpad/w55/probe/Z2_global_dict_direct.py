# pycsl-flags: --memory-model hoare
from typing import Dict

_G: Dict[int, int] = {1: 1}


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    _G[1] = 2
    return _G[1]

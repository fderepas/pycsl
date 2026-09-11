# pycsl-flags: --memory-model hoare
from typing import Dict


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f(k: int) -> int:
    d: Dict[int, int] = {1: 1}
    d[k] = 2
    return len(d)

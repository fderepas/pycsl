# pycsl-flags: --memory-model hoare
from typing import Dict


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f(c: int) -> int:
    d: Dict[int, int] = {1: 1}
    if c > 0:
        d[2] = 2
    return len(d)

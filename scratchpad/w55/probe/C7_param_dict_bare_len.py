# pycsl-flags: --memory-model hoare
from typing import Dict


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f(d: Dict[int, int]) -> int:
    return len(d)

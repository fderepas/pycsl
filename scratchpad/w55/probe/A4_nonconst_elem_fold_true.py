# pycsl-flags: --memory-model hoare
from typing import Dict


#@ requires a == b
#@ ensures \result == 2
#@ assigns \nothing
def f(a: int, b: int) -> int:
    d: Dict[int, int] = {a: 1, b: 2}
    return d[a]

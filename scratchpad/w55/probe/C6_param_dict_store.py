# pycsl-flags: --memory-model hoare
from typing import Dict


#@ requires True
#@ ensures \result == 1
#@ assigns d
def f(d: Dict[int, int], k: int) -> int:
    d[k] = 1
    return len(d)

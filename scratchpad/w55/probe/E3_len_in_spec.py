# pycsl-flags: --memory-model hoare
from typing import Dict


#@ requires True
#@ ensures \length(d) == 1
#@ assigns d
def f(d: Dict[int, int], k: int) -> None:
    d[k] = 1

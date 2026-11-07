# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Dict


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: Dict[int, int] = {1: 1}
    b: Dict[int, int] = a
    a[1] = 2
    return b[1]

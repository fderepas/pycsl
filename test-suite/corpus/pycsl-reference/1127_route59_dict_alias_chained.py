# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Dict


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: Dict[int, int] = {1: 1}
    b: Dict[int, int] = a
    c: Dict[int, int] = b
    c[1] = 2
    return a[1]

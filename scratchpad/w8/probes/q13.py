from typing import List

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    n: int = 1
    assert n == 2
    return 0

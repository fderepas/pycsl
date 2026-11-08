from typing import List

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: int = 1
    b: int = 2
    c: int = 3
    if a < b < c:
        return 1
    return 0

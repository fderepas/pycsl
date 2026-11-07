from typing import List, Dict

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: int = 1
    b: int = 2
    a, b = b, a
    return a - 2

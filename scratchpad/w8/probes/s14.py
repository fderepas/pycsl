from typing import List, Dict

#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: int = -7
    return a % 3

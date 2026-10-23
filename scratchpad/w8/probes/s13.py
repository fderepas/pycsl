from typing import List, Dict

#@ requires True
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    a: int = -7
    return a // 2 + 9

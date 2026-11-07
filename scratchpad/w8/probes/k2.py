from typing import List, Dict

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {}
    d.clear()
    return 0

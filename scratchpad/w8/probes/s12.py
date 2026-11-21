from typing import List, Dict

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {}
    d[1] = 7
    del d[1]
    return 0

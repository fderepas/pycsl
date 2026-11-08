from typing import Dict

#@ requires True
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    d: Dict[int, int] = {}
    d[1] = 7
    del d[1]
    return d.get(1, 0)

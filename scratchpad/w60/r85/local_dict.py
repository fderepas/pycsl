from typing import Dict


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d = {1: 5}
    if 1 in d:
        return 1
    return 0

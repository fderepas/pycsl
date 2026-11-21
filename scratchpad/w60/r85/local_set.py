from typing import Set


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    s = {7}
    if 7 in s:
        return 1
    return 0

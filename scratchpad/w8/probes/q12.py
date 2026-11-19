from typing import List

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    n: int = 5
    if (m := n + 1) > 5:
        return m
    return 0

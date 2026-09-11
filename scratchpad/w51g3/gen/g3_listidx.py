from typing import List

#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: List[int] = [1, 2]
    return a[5]

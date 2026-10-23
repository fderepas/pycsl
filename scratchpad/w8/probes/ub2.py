from typing import List

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2, 3]
    for x in xs:
        xs.append(x)
    return 0

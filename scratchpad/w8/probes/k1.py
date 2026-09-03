from typing import List, Dict

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [0, 7]
    v: int = xs.pop()
    return xs[0]

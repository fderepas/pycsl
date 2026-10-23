from typing import List

#@ requires \length(ys) == 2 and ys[0] == 0
#@ ensures \result == 0
#@ assigns \nothing
def driver(ys: List[int]) -> int:
    ys.reverse()
    return ys[0]

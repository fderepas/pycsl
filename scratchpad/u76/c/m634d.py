from typing import List


#@ requires len(xs) >= 1
#@ ensures \result == 0
#@ assigns \nothing
def f(xs: List[int]) -> int:
    i = 0
    #@ loop invariant 0 <= i <= 1
    #@ loop variant 1 - i
    while i < 1:
        xs[0] = 5
        i = i + 1
    return 0

# u76 helper for witness 10522 (review rt84 F2, route #634): declares `assigns \nothing` but writes the list parameter element xs[0] in a loop (refused: PYCSL-FUNCTION-FRAME).
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

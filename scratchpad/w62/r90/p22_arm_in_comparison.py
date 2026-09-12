from typing import List
#@ requires \length(xs) == 2 && xs[0] == 5
#@ ensures \result == 7
#@ assigns \nothing
def f(xs: List[int]) -> int:
    if (xs[0] == 5) is True:
        return 7
    return 0

from typing import List

#@ requires True
#@ ensures \result == a
#@ assigns \nothing
def g(a: int) -> int:
    return a

#@ requires \length(xs) == 1 and xs[0] == 7
#@ ensures \result == 0
#@ assigns \nothing
def h(xs: List[int]) -> int:
    return g(*xs)

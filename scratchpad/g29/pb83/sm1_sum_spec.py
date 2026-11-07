from typing import List
_ = 0  # anchor


#@ requires \length(a) == 3
#@ ensures \result == \sum(a, 0, 3)
def total(a: List[int]) -> int:
    return 0


#@ ensures \result == 0
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    return total(xs)

from typing import List
_ = 0  # anchor


#@ requires \length(a) == 3
#@ ensures \result == 99
def total(a: List[int]) -> int:
    return 0


#@ ensures \result == 99
def probe() -> int:
    xs: List[int] = [1, 2, 3]
    return total(xs)

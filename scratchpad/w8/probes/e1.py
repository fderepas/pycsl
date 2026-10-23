from typing import List

#@ requires True
#@ ensures \result == a + b
#@ assigns \nothing
def g(a: int, b: int) -> int:
    return a + b

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def driver(args: List[int]) -> int:
    return g(*args)

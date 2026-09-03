import math

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f(a: int) -> int:
    return math.floor(1.5)

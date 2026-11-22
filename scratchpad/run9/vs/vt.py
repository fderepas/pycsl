#@ requires x >= 0
#@ ensures \result == x + 1
def inc(x: int) -> int:
    return x + 1


#@ requires x > 0 and x < 0
#@ ensures \result == 7
def bad(x: int) -> int:
    return 3


#@ ensures \result == 2 * x
def dbl(x: int) -> int:
    return x + x

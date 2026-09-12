#@ requires x == 1
#@ ensures \result == 0
def f(x: bool) -> int:
    if x is not True:
        return 1
    return 0

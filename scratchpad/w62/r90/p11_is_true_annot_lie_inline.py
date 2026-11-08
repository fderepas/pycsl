#@ requires x == 1
#@ ensures \result == 1
def f(x: bool) -> int:
    if x is True:
        return 1
    return 0

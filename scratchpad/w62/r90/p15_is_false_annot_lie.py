#@ requires x == 0
#@ ensures \result == 1
def f(x: bool) -> int:
    if x is False:
        return 1
    return 0

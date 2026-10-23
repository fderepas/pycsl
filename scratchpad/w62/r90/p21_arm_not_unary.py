#@ requires x == 0
#@ ensures \result == 7
#@ assigns \nothing
def f(x: int) -> int:
    if (not x) is True:
        return 7
    return 0

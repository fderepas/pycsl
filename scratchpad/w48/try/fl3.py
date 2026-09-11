#@ requires x == 1.5
#@ ensures \result == 0
#@ assigns \nothing
def f(x: float) -> int:
    if x == 1.50 and x == 15e-1 and x > 1.0:
        return 0
    return 1

#@ requires n > 0
#@ ensures \result == 1
#@ assigns \nothing
def g(n: int) -> int:
    return 1

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f(b: int) -> int:
    if b > 0:
        raise ValueError(g(1))
    return 0

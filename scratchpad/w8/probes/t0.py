#@ requires n > 0
#@ ensures \result == 1
#@ assigns \nothing
def g(n: int) -> int:
    return 1

#@ requires True
#@ ensures True
#@ assigns \nothing
def f() -> int:
    x: int = g(0)
    return x

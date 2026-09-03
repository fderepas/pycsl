#@ requires True
#@ ensures \result == 7
#@ assigns \nothing
def g(a: int) -> int:
    return a + 7

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    return g(0)

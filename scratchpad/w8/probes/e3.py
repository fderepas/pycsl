#@ requires True
#@ ensures \result == a
#@ assigns \nothing
def g(a: int) -> int:
    return a

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def h(*args: int) -> int:
    return g(*args)

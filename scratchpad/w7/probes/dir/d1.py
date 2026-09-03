#@ requires True
#@ no_exception all
#@ ensures \result >= 0
#@ assigns \nothing
def f(a: int, b: int) -> int:
    return a // b

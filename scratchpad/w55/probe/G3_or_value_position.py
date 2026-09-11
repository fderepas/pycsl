# pycsl-flags: --memory-model hoare

#@ requires a == 0
#@ requires b == 5
#@ ensures \result == 5
#@ assigns \nothing
def f(a: int, b: int) -> int:
    return a or b

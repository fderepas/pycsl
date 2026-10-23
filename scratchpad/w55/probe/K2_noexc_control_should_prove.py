# pycsl-flags: --memory-model hoare

#@ no_exception ZeroDivisionError
#@ requires b != 0
#@ ensures True
#@ assigns \nothing
def f(a: int, b: int) -> int:
    return a // b

# pycsl-flags: --memory-model hoare

#@ no_exception ZeroDivisionError
#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f(a: int) -> int:
    return a // 0

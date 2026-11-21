# pycsl-flags: --memory-model hoare

#@ requires True
#@ no_exception \all
#@ ensures True
#@ assigns \nothing
def f(a: int) -> int:
    x = float(a)
    return 0

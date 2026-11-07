# pycsl-flags: --memory-model hoare

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    return f(n)

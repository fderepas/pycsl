# pycsl-flags: --memory-model hoare

#@ requires True
#@ ensures \result == 5
#@ assigns \nothing
def f(c: int) -> int:
    if c > 0:
        return 5

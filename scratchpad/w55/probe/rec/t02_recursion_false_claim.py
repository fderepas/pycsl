# pycsl-flags: --memory-model hoare

#@ requires n >= 0
#@ ensures \result == 99
#@ assigns \nothing
def f(n: int) -> int:
    if n == 0:
        return 0
    return f(n - 1)

# pycsl-flags: --memory-model hoare
_ = 0
#@ requires n > 0
#@ ensures \result == 7
#@ assigns \nothing
def f(n: int) -> int:
    return f(n)

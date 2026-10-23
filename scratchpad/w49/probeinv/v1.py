# pycsl-flags: --memory-model hoare
_ = 0
#@ requires False
#@ ensures \result == 7
#@ assigns \nothing
def f(x: int) -> int:
    return 0

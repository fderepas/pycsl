# pycsl-flags: --memory-model hoare
_ = 0
#@ requires x == 100
#@ ensures \result == 7
#@ assigns \nothing
def f(x: int) -> int:
    if 0 <= x <= 3:
        return 7
    return 0

# pycsl-flags: --memory-model hoare
_ = 0
#@ requires x == 100
#@ ensures \result == 7
#@ assigns \nothing
def f(x: int) -> int:
    b = 0 <= x <= 3
    if b:
        return 7
    return 0

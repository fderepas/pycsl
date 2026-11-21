# pycsl-flags: --memory-model hoare
_ = 0
#@ requires x == 0.1
#@ ensures \result == 0.3
#@ assigns \nothing
def f(x: float) -> float:
    return x + 0.2

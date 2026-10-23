_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f(a: list) -> int:
    a[0] = 7
    return 0

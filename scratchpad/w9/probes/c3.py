_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
def f() -> int:
    x = 0
    #@ check x == 99
    return x

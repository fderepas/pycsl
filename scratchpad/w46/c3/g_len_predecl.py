_ = 0  # anchor
#@ requires c == 0
#@ ensures \result == 2
#@ assigns \nothing
def f(c: int) -> int:
    a = [0]
    if c == 0:
        a = [9, 9, 9]
    else:
        a = [1, 2]
    return len(a)

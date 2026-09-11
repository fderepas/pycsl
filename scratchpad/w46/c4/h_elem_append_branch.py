_ = 0  # anchor
#@ requires c == 0
#@ ensures \result == 1
#@ assigns \nothing
def f(c: int) -> int:
    a = []
    if c == 0:
        a.append(9)
    else:
        a.append(1)
    return a[0]

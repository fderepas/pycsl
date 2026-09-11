_ = 0  # anchor
#@ requires c == 0
#@ ensures \result == 2
#@ assigns \nothing
def f(c: int) -> int:
    a = []
    if c == 0:
        a.append(9)
        a.append(9)
        a.append(9)
    else:
        a.append(1)
        a.append(2)
    return len(a)

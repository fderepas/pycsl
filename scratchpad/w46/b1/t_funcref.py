_ = 0  # anchor
def g() -> int:
    return 1


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = g
    if x:
        return 7
    return 0

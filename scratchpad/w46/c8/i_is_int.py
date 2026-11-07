_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 1000
    y = 1000
    if x is y:
        return 7
    return 0

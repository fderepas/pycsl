_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 1
    if x is True:
        return 7
    return 0

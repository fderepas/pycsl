_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = (1).__class__
    if x == 0:
        return 7
    return 0

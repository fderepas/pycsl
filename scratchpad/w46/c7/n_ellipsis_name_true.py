_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = ...
    if x is Ellipsis:
        return 0
    return 1

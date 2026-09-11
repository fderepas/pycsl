_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = lambda y: y
    if x:
        return 7
    return 0

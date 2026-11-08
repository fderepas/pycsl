_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = slice(0, 1)
    if x:
        return 7
    return 0

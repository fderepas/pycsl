_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 1
    y = x
    x += 1
    if y == 2:
        return 7
    return 0

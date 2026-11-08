_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = [1, 2].copy()
    if x == 0:
        return 7
    return 0

_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = (i for i in [1, 2, 3])
    if x == 0:
        return 7
    return 0

_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    a, b = (1, 2), (3, 4)
    if a == 0:
        return 7
    return 0

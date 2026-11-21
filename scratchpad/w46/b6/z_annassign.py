_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x: int = (1, 2)
    if x == 0:
        return 7
    return 0

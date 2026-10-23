_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    if (1, 2):
        return 7
    return 0

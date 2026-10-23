_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    if ...:
        return 7
    return 0

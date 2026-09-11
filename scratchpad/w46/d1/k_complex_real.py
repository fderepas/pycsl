_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 1 + 2j
    if x == 1:
        return 7
    return 0

_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = {i for i in [1, 2]}
    if x:
        return 7
    return 0

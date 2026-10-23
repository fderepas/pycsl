_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 0
    i = 0
    while i < 1:
        x = (1, 2)
        i = i + 1
    if x == 0:
        return 7
    return 0

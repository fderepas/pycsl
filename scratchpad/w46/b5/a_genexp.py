_ = 0  # anchor
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    x = (i for i in [1, 2, 3])
    return x + 5

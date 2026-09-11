_ = 0  # anchor
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    x = (1, 2)
    return x + 5

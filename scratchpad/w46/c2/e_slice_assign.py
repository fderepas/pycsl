_ = 0  # anchor
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a = [1, 2, 3]
    a[0:2] = [7, 8]
    return a[0]

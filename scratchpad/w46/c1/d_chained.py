_ = 0  # anchor
count = 0


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a = 1
    b = 2
    c = 3
    if a < b < c:
        return 1
    return 0

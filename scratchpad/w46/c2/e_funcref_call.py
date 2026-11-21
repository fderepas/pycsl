_ = 0  # anchor
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return 1


#@ ensures \result == 2
#@ assigns \nothing
def h() -> int:
    return 2


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    k = h
    return k()

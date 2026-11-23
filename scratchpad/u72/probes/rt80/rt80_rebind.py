#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1

#@ ensures \result == 2
#@ assigns \nothing
def h() -> int:
    return 2

f = h

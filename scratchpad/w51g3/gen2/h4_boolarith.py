#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if True + True == 2:
        return 1
    return 0

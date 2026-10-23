#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if 1 < 2 < 3:
        return 1
    return 0

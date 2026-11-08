#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 0
    if x is False:
        return 7
    return 0

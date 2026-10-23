#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    if True is True:
        return 7
    return 0

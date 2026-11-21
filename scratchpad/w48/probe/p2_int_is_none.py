#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 0
    if x is None:
        return 7
    return 0

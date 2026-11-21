#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = None
    if x == 0:
        return 7
    return 0

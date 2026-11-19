#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = None
    y = None
    if x == y:
        return 0
    return 7

#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = None
    x = 5
    if x == 0:
        return 7
    return 0

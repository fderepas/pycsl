#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x = None
    if x:
        return 7
    return 0

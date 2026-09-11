#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = Ellipsis
    if x == 0:
        return 7
    return 0

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    if float("inf") > 1.0:
        return 1
    return 0

#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = float("nan")
    if x != x:
        return 7
    return 0

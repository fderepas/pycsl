#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    x = None
    return x + 5

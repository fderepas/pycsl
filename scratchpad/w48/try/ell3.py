#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    x = Ellipsis
    return x + 5

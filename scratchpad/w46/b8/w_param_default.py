_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def g(x: int = (1, 2)) -> int:
    if x == 0:
        return 7
    return 0


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    return g()

#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    x: float = 1.5
    y: float = 1.50
    if x == y:
        return 0
    return 1

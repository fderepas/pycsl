#@ ensures \result == 7
#@ assigns \nothing
def f(x: int, y: int) -> int:
    if (x == y) is True:
        if x == y:
            return 7
        return 1
    return 7

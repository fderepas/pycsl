#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    r = 0
    s = 0
    match x:
        case y:
            r = y
    match x + 1:
        case y:
            s = y
    return r - s

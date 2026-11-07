#@ requires 0 <= n and n <= 5
#@ ensures \result == 0
#@ assigns \nothing
def f(n: int) -> int:
    r: int = 0
    match n:
        case 1 | 2:
            r = 7
        case _:
            r = 0
    return r

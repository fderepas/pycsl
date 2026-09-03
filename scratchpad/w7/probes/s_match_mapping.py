#@ requires 0 <= n and n <= 5
#@ ensures \result == 9
#@ assigns \nothing
def f(n: int) -> int:
    r: int = 9
    match n:
        case 0:
            r = 1
        case _:
            r = 9
    return r

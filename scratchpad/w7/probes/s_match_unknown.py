#@ requires 0 <= n and n <= 5
#@ ensures \result == 7
#@ assigns \nothing
def f(n: int) -> int:
    r: int = 0
    match n:
        case {"a": 1}:
            r = 7
        case _:
            r = 0
    return r

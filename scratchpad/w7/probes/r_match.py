#@ requires 0 <= n and n <= 5
#@ ensures \result >= 0
#@ assigns \nothing
def f(n: int) -> int:
    m: int = n
    #@ assert 1 == 2
    match m:
        case 0:
            m = 1
        case _:
            m = 2
    return m

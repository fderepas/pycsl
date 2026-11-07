#@ requires 0 <= n and n <= 5
#@ ensures \result >= 0
#@ assigns \nothing
def f(n: int) -> int:
    m: int = n
    #@ assert 1 == 2
    if m > 100: m = 0
    return m

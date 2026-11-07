#@ ensures \result == n
#@ no_exception \all
def g(n: int) -> int:
    return n


#@ requires -1000 <= n and n <= 1000
#@ no_exception \all
def f(n: int) -> int:
    y: int = g(n)
    x = float(y)
    return 0

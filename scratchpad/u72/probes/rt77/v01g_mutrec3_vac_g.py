#@ requires n >= 0
#@ ensures \result >= 0
#@ \variant n
#@ assigns \nothing
def f(n: int) -> int:
    if n <= 0:
        return 0
    return g(n - 1)

#@ requires n >= 0 and n < 0
#@ ensures \result == 99
#@ \variant n
#@ assigns \nothing
def g(n: int) -> int:
    if n <= 0:
        return 0
    if n < 0 and n > 0:
        return h(n - 1)
    return f(n - 1)

#@ requires n >= 0
#@ ensures \result >= 0
#@ \variant n
#@ assigns \nothing
def h(n: int) -> int:
    if n <= 0:
        return 1
    return f(n - 1)

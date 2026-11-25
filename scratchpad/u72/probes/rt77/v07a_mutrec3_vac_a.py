#@ requires n >= 0 and n < 0
#@ ensures \result == 99
#@ \variant n
#@ assigns \nothing
def a(n: int) -> int:
    if n <= 0:
        return 0
    return b(n - 1) + c(n - 1)

#@ requires n >= 0
#@ ensures \result >= 0
#@ \variant n
#@ assigns \nothing
def b(n: int) -> int:
    if n <= 0:
        return 0
    return a(n - 1)

#@ requires n >= 0
#@ ensures \result >= 0
#@ \variant n
#@ assigns \nothing
def c(n: int) -> int:
    if n <= 0:
        return 1
    return a(n - 1)

#@ requires x >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def use(x: int) -> int:
    return a(x)

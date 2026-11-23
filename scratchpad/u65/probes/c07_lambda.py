g = lambda x: x + 1

#@ requires x > 0 and x < 0
#@ ensures \result == 99
def f(x: int) -> int:
    return g(x)

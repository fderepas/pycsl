#@ \diverges
def f(x: int) -> int:
    while True:
        pass
    return 0


#@ requires x > 0 and x < 0
#@ ensures \result == 99
def f(x: int) -> int:
    return 1

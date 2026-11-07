#@ requires x < 0
#@ ensures \result == 5
def f(x: int) -> int:
    if x > 0:
        return 5

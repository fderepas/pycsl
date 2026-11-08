#@ requires x < 0
#@ ensures \result == 5
def f(x: int) -> str:
    if x > 0:
        return "a"

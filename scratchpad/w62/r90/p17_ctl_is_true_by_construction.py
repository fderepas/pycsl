#@ requires a > b
#@ ensures \result == 1
def f(a: int, b: int) -> int:
    y = a > b
    if y is True:
        return 1
    return 0

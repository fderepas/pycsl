_ = 0  # anchor


#@ requires a == 7 and b == 0 - 3
#@ ensures \result == 0
def f(a: int, b: int) -> int:
    return a % b


#@ ensures \result == 0
def probe() -> int:
    return f(7, 0 - 3)

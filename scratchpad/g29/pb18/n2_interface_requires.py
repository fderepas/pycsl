_ = 0  # anchor


#@ requires x > 0
#@ interface requires x >= 0
#@ ensures \result == 10 // x
def f(x: int) -> int:
    return 10 // x


#@ ensures \result == 0
def probe() -> int:
    return f(0) * 0

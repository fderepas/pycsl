_ = 0  # anchor


#@ ensures \result >= 0
#@ interface ensures \result == 7
def f(x: int) -> int:
    if x > 0:
        return x
    return 0


#@ ensures \result == -1
def probe() -> int:
    return f(3)

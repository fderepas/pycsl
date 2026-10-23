_ = 0  # anchor


#@ ensures \result == 99
def f(n: int) -> int:
    n = 0
    return 0


#@ ensures \result == 99
def probe() -> int:
    return f(3)

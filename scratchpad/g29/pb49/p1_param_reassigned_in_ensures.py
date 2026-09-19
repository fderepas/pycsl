_ = 0  # anchor


#@ ensures \result == n
def f(n: int) -> int:
    n = 0
    return 0


#@ ensures \result == 3
def probe() -> int:
    return f(3)

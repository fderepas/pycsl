_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    a: int = 2
    b: int = 3
    return a * b

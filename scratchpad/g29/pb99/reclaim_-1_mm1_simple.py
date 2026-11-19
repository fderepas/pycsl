_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    a: int = 2
    b: int = 3
    return a * b

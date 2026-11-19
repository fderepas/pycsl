_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    a: int = 1
    b: int = 2
    a, b = b, a
    return b

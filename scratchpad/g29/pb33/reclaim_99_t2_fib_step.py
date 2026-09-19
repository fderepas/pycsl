_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    a: int = 1
    b: int = 2
    a, b = b, a + b
    return b

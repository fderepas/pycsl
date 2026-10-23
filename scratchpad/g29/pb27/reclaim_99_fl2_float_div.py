_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    a: float = 1.0
    b: float = 3.0
    c: float = a / b
    if c * 3.0 == 1.0:
        return 1
    return 0

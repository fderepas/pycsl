_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    a: float = 0.1
    b: float = 0.2
    if a + b == 0.3:
        return 1
    return 0

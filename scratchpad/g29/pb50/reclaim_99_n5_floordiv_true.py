_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    a: int = 7
    b: int = 0 - 3
    return a // b

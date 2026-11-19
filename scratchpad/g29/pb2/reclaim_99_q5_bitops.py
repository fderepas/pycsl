_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    a: int = -1
    return a & 3

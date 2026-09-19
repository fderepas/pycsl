_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    a: int = -1
    return a & 3

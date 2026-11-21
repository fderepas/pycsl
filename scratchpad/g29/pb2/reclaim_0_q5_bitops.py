_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    a: int = -1
    return a & 3

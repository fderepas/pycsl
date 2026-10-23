_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    a: int = -5
    return abs(a)

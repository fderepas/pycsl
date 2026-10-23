_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    a: int = -5
    return abs(a)

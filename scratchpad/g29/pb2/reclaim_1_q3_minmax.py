_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    a: int = -3
    b: int = 2
    return min(a, b) + max(a, b)

_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    a: int = 0 - 7
    b: int = 3
    return a % b

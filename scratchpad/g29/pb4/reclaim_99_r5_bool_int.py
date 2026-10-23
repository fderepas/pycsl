_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    b: bool = True
    return b + 1

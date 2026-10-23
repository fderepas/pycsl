_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    b: bool = True
    return b + 1

_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    a = b = 7
    return a + b

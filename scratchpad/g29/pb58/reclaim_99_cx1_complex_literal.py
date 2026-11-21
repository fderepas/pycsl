_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    z = 0 + 3j
    if z == 0:
        return 1
    return 0

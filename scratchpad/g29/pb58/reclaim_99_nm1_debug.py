_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    if __debug__:
        return 1
    return 0

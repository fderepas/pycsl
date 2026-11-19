_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    if __debug__:
        return 1
    return 0

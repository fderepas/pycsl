_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    x = Ellipsis
    if x == 0:
        return 1
    return 0

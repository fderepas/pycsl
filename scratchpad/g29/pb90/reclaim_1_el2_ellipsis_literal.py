_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    x = ...
    if x == 0:
        return 1
    return 0

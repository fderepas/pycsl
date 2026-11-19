_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    return max(x for x in [1, 2, 3])

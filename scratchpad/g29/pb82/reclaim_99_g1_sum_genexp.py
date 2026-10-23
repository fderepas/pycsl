_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    return sum(x for x in [1, 2, 3])

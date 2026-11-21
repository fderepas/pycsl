_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    return sum([x for x in [1, 2, 3]])

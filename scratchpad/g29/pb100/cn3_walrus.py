_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    if (n := 5) > 3:
        return n
    return 0

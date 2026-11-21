_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s: str = "%d" % 7
    return len(s)

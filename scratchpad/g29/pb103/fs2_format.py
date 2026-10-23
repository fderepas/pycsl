_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s: str = "{}".format(7)
    return len(s)

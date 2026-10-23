_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    s: str = "abc"
    t: str = s[:2]
    return len(t)

_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    s: str = "abc"
    t: str = s[:2]
    return len(t)

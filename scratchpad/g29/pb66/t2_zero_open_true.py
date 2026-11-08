_ = 0  # anchor


#@ ensures \result == 3
def probe() -> int:
    s: str = "abc"
    t: str = s[0:]
    return len(t)

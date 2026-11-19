_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    s: str = "abc"
    t: str = s[0 - 2:]
    return len(t)

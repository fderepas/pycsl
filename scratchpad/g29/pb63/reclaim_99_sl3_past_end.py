_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    s: str = "abc"
    t: str = s[5:7]
    return len(t)

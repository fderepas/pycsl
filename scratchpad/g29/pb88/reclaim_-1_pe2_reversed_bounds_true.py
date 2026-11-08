_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    s: str = "abc"
    t: str = s[3:1]
    return len(t)

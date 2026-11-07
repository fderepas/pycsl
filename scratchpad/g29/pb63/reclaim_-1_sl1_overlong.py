_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    s: str = "abc"
    t: str = s[1:10]
    return len(t)

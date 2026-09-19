_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    s: str = "abcd"
    t: str = s[::2]
    return len(t)

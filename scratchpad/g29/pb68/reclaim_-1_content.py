_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    s: str = "abc"
    t: str = s[1:]
    if t == "bc":
        return 1
    return 0

_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    s: str = "abc"
    t: str = s[::0 - 1]
    if t == "abc":
        return 1
    return 0

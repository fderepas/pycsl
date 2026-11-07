_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s: str = "hello"
    t: str = s[1:3]
    return len(t) + 1

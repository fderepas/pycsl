_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s: str = "aaa"
    t: str = s.replace("a", "bb")
    return len(t)

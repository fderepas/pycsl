_ = 0  # anchor


#@ no_exception IndexError
#@ ensures \result == 0
def probe() -> int:
    s: str = "abc"
    i: int = 5
    t: str = s[i]
    return len(t) - 1

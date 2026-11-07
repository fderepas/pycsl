_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    s: str = "x"
    if s:
        return 1
    return 0

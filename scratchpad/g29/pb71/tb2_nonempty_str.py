_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s: str = "x"
    if s:
        return 1
    return 0

_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    s: str = "é"
    return len(s)

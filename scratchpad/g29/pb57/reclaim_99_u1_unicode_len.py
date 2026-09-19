_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    s: str = "é"
    return len(s)

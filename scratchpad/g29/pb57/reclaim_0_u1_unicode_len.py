_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s: str = "é"
    return len(s)

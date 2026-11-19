_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    s: str = "é"
    return len(s)

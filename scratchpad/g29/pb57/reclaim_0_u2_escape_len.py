_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s: str = "\n\t"
    return len(s)

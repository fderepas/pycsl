_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    s: str = ""
    if s:
        return 1
    return 0

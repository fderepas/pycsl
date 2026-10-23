_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    s: str = "abc"
    if s.startswith("b"):
        return 1
    return 0

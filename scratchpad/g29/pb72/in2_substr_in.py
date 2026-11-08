_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s: str = "abc"
    if "b" in s:
        return 1
    return 0

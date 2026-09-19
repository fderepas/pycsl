_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    a: str = "Z"
    b: str = "a"
    if a < b:
        return 1
    return 0

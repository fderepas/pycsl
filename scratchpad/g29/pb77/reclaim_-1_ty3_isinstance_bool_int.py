_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    b: bool = True
    if isinstance(b, int):
        return 1
    return 0

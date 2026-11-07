_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    b: bool = True
    if isinstance(b, int):
        return 1
    return 0

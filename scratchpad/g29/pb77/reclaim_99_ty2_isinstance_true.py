_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    x: int = 5
    if isinstance(x, int):
        return 1
    return 0

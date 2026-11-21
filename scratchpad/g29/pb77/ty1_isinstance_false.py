_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    x: int = 5
    if isinstance(x, str):
        return 1
    return 0

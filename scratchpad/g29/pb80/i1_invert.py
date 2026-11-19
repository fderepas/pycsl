_ = 0  # anchor


#@ ensures \result == 0 - 5
def probe() -> int:
    x: int = 5
    return ~x

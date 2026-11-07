_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    n: int = 0
    try:
        n = 1
    finally:
        n = 9
    return n

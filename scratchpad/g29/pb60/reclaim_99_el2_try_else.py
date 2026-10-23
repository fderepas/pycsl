_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    n: int = 0
    try:
        n = 1
    except ValueError:
        n = 2
    else:
        n = 3
    return n

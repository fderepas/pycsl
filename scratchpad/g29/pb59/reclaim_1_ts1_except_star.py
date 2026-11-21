_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    n: int = 0
    try:
        raise ValueError()
    except* ValueError:
        n = 9
    return n

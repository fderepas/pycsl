_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    n: int = 1
    #@ ghost n = 5
    return n

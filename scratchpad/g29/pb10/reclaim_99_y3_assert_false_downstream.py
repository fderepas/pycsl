_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    n: int = 1
    #@ check n == 1
    return n

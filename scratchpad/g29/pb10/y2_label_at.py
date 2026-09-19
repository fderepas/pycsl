_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    n: int = 1
    #@ label L
    n = 2
    #@ assert \at(n, L) == 2
    return n - 2

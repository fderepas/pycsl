_ = 0  # anchor

K: int = 3
K = 5


#@ ensures \result == -1
def probe() -> int:
    return K

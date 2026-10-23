_ = 0  # anchor

K: int = 3
K = 5


#@ ensures \result == 3
def probe() -> int:
    return K

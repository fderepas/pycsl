_ = 0  # anchor

J: int = 2
K: int = J + 10


#@ ensures \result == 99
def probe() -> int:
    return K

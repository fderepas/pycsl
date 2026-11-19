_ = 0  # anchor

LIMIT: int = 10


#@ ensures \result == LIMIT
def probe() -> int:
    return 3

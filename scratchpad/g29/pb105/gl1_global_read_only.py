_ = 0  # anchor

LIMIT: int = 10


#@ ensures \result == 0
def probe() -> int:
    return LIMIT

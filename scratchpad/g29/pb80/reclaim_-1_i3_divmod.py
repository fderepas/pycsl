_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    q, r = divmod(7, 2)
    return q + r

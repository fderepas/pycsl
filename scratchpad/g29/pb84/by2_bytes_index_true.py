_ = 0  # anchor


#@ ensures \result == 97
def probe() -> int:
    b: bytes = b"abc"
    return b[0]

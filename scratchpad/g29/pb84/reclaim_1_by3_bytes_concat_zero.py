_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    b: bytes = b"ab" + b"cd"
    return len(b)

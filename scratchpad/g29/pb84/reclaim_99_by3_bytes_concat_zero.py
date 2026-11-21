_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    b: bytes = b"ab" + b"cd"
    return len(b)

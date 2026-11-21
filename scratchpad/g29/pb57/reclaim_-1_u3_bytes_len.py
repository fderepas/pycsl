_ = 0  # anchor


#@ ensures \result == -1
def probe() -> int:
    b: bytes = b"\x00ab"
    return len(b)
